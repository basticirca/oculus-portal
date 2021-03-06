#!/usr/bin/python

import avango
import avango.script
from avango.script import field_has_changed
import avango.gua
import time
import math

from examples_common.GuaVE import GuaVE

from ..Navigation import *

class PortalPicker(avango.script.Script):
  SceneGraph = avango.gua.SFSceneGraph()
  Ray        = avango.gua.SFRayNode()
  Options    = avango.SFInt()
  Mask       = avango.SFString()
  Results    = avango.gua.MFPickResult()

  def __init__(self):
    self.super(PortalPicker).__init__()
    self.always_evaluate(True)

    self.SceneGraph.value = avango.gua.nodes.SceneGraph()
    self.Ray.value  = avango.gua.nodes.RayNode()
    self.Options.value = avango.gua.PickingOptions.PICK_ONLY_FIRST_OBJECT \
                         | avango.gua.PickingOptions.PICK_ONLY_FIRST_FACE
    self.Mask.value = ""
    
  def evaluate(self):
    results = self.SceneGraph.value.ray_test(self.Ray.value,
                                             self.Options.value,
                                             self.Mask.value)
    self.Results.value = results.value

class UpdatePortalTransform(avango.script.Script):

  PortalTransformIn     = avango.gua.SFMatrix4()
  ViewTransformIn       = avango.gua.SFMatrix4()
  ViewTransformOut      = avango.gua.SFMatrix4()

  def __init__(self):
    self.super(UpdatePortalTransform).__init__()
    self.NAME = ""
    
  def my_constructor(self, NAME):
    self.NAME = NAME

  def evaluate(self):
    self.ViewTransformOut.value = avango.gua.make_inverse_mat(self.PortalTransformIn.value) * \
                                    self.ViewTransformIn.value

class PortalController(avango.script.Script):
  PickedPortals     = avango.gua.MFPickResult()
  sfUserHead        = avango.gua.SFMatrix4()
  
  def __init__(self):
    self.super(PortalController).__init__()
    self.NAME           = ""
    self.ACTIVESCENE    = avango.gua.nodes.SceneGraph()
    self.PORTALPICKER   = PortalPicker()
    self.PIPELINE       = avango.gua.nodes.Pipeline()
    self.PORTALS        = []
    self.PORTALCUBES    = []
    self.ACTIVEPORTALS  = []
    self.NAVIGATION     = Navigation()
    self.PORTALUPDATERS = []
    self.PLATFORM       = -1
    self.USERHEAD       = avango.gua.nodes.TransformNode()
    
  def my_constructor(self, ACTIVESCENE, NAME, VIEWINGPIPELINES, PIPELINE, PORTALS, PORTALCUBES, NAVIGATION, USERHEAD):
    self.NAME             = NAME
    self.ACTIVESCENE      = ACTIVESCENE
    self.VIEWINGPIPELINES = VIEWINGPIPELINES
    self.PIPELINE         = PIPELINE
    self.PORTALS          = PORTALS
    self.PORTALCUBES      = PORTALCUBES

    for p_cube in self.PORTALCUBES:
      for portal in p_cube.Portals:
        self.PORTALS.append(portal)
    
    self.ACTIVEPORTALS    = self.create_active_portals()      
    self.NAVIGATION       = NAVIGATION

    # references
    self.USERHEAD         = USERHEAD
        
    self.create_portal_updaters()     

    self.initialize_portal_group_names()
    self.update_prepipes()
    self.update_portal_picker()

    self.always_evaluate(True) # set class evaluation policy


  @field_has_changed(PickedPortals)
  def evaluate_scene_change(self):
    _platform = self.ACTIVESCENE["/platform_" + str(self.PLATFORM)]
    _pos_p1 = _platform.Transform.value.get_translate()

    for portal in self.PickedPortals.value:
      if portal.Distance.value < 0.5:
        for p in self.ACTIVEPORTALS:
          if p.GEOMETRY.Name.value == portal.Object.value.Name.value:
            _pos_p2 = p.GEOMETRY.Transform.value.get_translate()
            _distance_x = _pos_p1.x - _pos_p2.x
            _distance_y = _pos_p1.y - _pos_p2.y
            self.change_scene(p, _distance_x, _distance_y)
            break
        break

  def evaluate(self):
    self.sfUserHead.value = self.USERHEAD.WorldTransform.value

    for p_cube in self.PORTALCUBES:
      if p_cube.visibility_updated == True:
        
        if p_cube.sf_visibility.value == False:
          for c_portal in p_cube.Portals:
            portal = next((p for p in self.PORTALS if c_portal.NAME == p.NAME), None)
            if "do_not_display_group" not in portal.GEOMETRY.GroupNames.value:
              portal.GEOMETRY.GroupNames.value.append("do_not_display_group")
            if portal in self.ACTIVEPORTALS:
              self.ACTIVEPORTALS.remove(portal)

        else: # p_cube.sf_visibility.value == True
          for c_portal in p_cube.Portals:
            portal = next((p for p in self.PORTALS if c_portal.NAME == p.NAME), None)
            if "do_not_display_group" in portal.GEOMETRY.GroupNames.value:
              portal.GEOMETRY.GroupNames.value.remove("do_not_display_group")
            if portal not in self.ACTIVEPORTALS:
              self.ACTIVEPORTALS.append(portal)

        p_cube.visibility_updated = False
        
    #self.adjust_nearplane()
    
  def change_scene(self, PORTAL, DISTANCE_X, DISTANCE_Y):
    _platform = self.ACTIVESCENE["/platform_" + str(self.PLATFORM)]
    _rotate_old_scene = _platform.Transform.value.get_rotate()

    PORTAL.EXITSCENE.Root.value.Children.value.append(_platform)

    self.PIPELINE.Camera.value.SceneGraph.value = PORTAL.EXITSCENE.Name.value

    for view_pipe in self.VIEWINGPIPELINES.value:
      if view_pipe == self.PIPELINE:
        view_pipe.Camera.value = self.PIPELINE.Camera.value

    PORTAL.ENTRYSCENE.Root.value.Children.value.remove(_platform)

    self.ACTIVESCENE = PORTAL.EXITSCENE

    # Starting Position
    new_pos = avango.gua.make_trans_mat(PORTAL.EXITPOS.get_translate().x + DISTANCE_X, 
                                        PORTAL.EXITPOS.get_translate().y + DISTANCE_Y,
                                        PORTAL.EXITPOS.get_translate().z)   
    # Starting Rotation
    new_rot = avango.gua.make_rot_mat(_rotate_old_scene)

    self.NAVIGATION.set_to_pos(new_pos * new_rot)

    head_trans = self.USERHEAD.Transform.value.get_translate()
    self.USERHEAD.Transform.value = avango.gua.make_trans_mat(head_trans.x, head_trans.y, head_trans.z)

    self.ACTIVEPORTALS  = self.create_active_portals()

    self.create_portal_updaters()
    self.update_portal_picker()

  def create_portal_updaters(self):
    self.PORTALUPDATERS = []
    
    for p in self.ACTIVEPORTALS:
      self.PORTALUPDATERS.append(UpdatePortalTransform())
      self.PORTALUPDATERS[len(self.PORTALUPDATERS) - 1].my_constructor(p.NAME + "_updater")
      self.PORTALUPDATERS[len(self.PORTALUPDATERS) - 1].PortalTransformIn.connect_from(p.sf_portal_pos)
      self.PORTALUPDATERS[len(self.PORTALUPDATERS) - 1].ViewTransformIn.connect_from(self.sfUserHead)
      p.EXITSCENE[p.HEAD].Transform.connect_from(self.PORTALUPDATERS[len(self.PORTALUPDATERS) - 1].ViewTransformOut)
    
  def create_active_portals(self):
    activeportals = []
    
    for p in self.PORTALS:
      if p.ENTRYSCENE.Name.value == self.ACTIVESCENE.Name.value and "do_not_display_group" not in p.GEOMETRY.GroupNames.value:
        activeportals.append(p)
        
    return activeportals
      
  def update_prepipes(self):
    pre_pipes = []      
    for p in self.PORTALS:
      pre_pipes.append(p.PRE_PIPE)

    self.PIPELINE.PreRenderPipelines.value = pre_pipes

  def initialize_portal_group_names(self):
    for p in self.PORTALS:
      p.GEOMETRY.GroupNames.value.append(self.NAME + "portals")

  def adjust_nearplane(self):
    for p in self.ACTIVEPORTALS:
      _pos_p1 = p.EXITSCENE["/" + p.NAME + "Screen"].Transform.value.get_translate().z
      _pos_p2 = p.EXITSCENE["/" + p.NAME + "Screen/head"].Transform.value.get_translate().z
      _distance = abs (_pos_p1 - _pos_p2)
      p.PRE_PIPE.NearClip.value = _distance
  
  def update_portal_picker(self):
    self.PORTALPICKER.Mask.value = self.PORTALS[0].GROUPNAME
    self.PORTALPICKER.SceneGraph.value = self.ACTIVESCENE
    self.USERHEAD.Children.value.append(self.PORTALPICKER.Ray.value)
    self.PickedPortals.connect_from(self.PORTALPICKER.Results)

  def delete_portal_group_name(self, GROUPNAME):
    for p in self.PORTALS:
      p.GEOMETRY.GroupNames.value.remove(GROUPNAME)
