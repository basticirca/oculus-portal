#!/usr/bin/python

import avango
import avango.script
from avango.script import field_has_changed
import avango.gua
import time
import math

import examples_common.navigator
from examples_common.GuaVE import GuaVE

class Portal(avango.script.Script):

    # init fields
    sf_portal_pos = avango.gua.SFMatrix4()

    def __init__(self):
        self.super(Portal).__init__()
        self.NAME           = ""
        self.ENTRYSCENE     = avango.gua.nodes.SceneGraph()
        self.EXITSCENE      = avango.gua.nodes.SceneGraph()
        self.EXITPOS        = avango.gua.Mat4()
        self.WIDTH          = 0
        self.HEIGHT         = 0
        self.PRE_PIPE       = avango.gua.nodes.Pipeline()
        self.GEOMETRY       = avango.gua.nodes.GeometryNode()
        self.HEAD           = ""


    def my_constructor(self, NAME, ENTRYSCENE, EXITSCENE, PORTALPOS, EXITPOS, WIDTH, HEIGHT):
        self.sf_portal_pos.value    = PORTALPOS
        self.NAME                   = NAME
        self.ENTRYSCENE             = ENTRYSCENE
        self.EXITSCENE              = EXITSCENE
        self.EXITPOS                = EXITPOS
        self.WIDTH                  = WIDTH
        self.HEIGHT                 = HEIGHT
        self.PRE_PIPE               = self.create_default_pipe()
        self.GEOMETRY               = self.create_geometry(PORTALPOS)
        self.HEAD                   = "/" + self.NAME + "Screen/head"

    def create_default_pipe(self):
        self.create_camera()
        
        width   = 1920
        height  = int(width * 9.0 / 16.0)
        size    = avango.gua.Vec2ui(width, height)

        camera = avango.gua.nodes.Camera(LeftEye    = "/" + self.NAME + "Screen/head" + "/mono_eye",
                                        RightEye    = "/" + self.NAME + "Screen/head" + "/mono_eye",
                                        LeftScreen  = "/" + self.NAME + "Screen",
                                        RightScreen = "/" + self.NAME + "Screen",
                                        SceneGraph  = self.EXITSCENE.Name.value)

        pre_pipe = avango.gua.nodes.Pipeline(Camera = camera,
                                            OutputTextureName = self.NAME + "Texture")

        pre_pipe.LeftResolution.value  = avango.gua.Vec2ui(width/2, height/2)
        pre_pipe.EnableStereo.value = False
        pre_pipe.BackgroundTexture.value = "data/textures/sky.jpg"
        pre_pipe.EnableBackfaceCulling.value = True

        return pre_pipe

    def create_geometry(self, PORTALPOS):
        loader = avango.gua.nodes.GeometryLoader()
        

        geometry = loader.create_geometry_from_file(self.NAME + "Node",
                                                "data/objects/plane.obj",
                                                "Portal" + self.NAME,
                                                avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)

        geometry.Transform.value = PORTALPOS *\
                                avango.gua.make_rot_mat(90, 1.0, 0.0, 0.0) *\
                                avango.gua.make_rot_mat(180, 0.0, 1.0, 0.0) *\
                                avango.gua.make_scale_mat(self.WIDTH, 1.0, self.HEIGHT)

        avango.gua.set_material_uniform(  "Portal" + self.NAME,
                                          "portal_texture",
                                          self.NAME + "Texture")

        self.ENTRYSCENE.Root.value.Children.value.append(geometry)
        
        return geometry

    def create_camera(self):
        screen = avango.gua.nodes.ScreenNode(Name   = self.NAME + "Screen", 
                                            Width   = self.WIDTH,
                                            Height  = self.HEIGHT)

        screen.Transform.value = self.EXITPOS

        head = avango.gua.nodes.TransformNode(Name = "head")
        head.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, 1.7)

        mono_eye = avango.gua.nodes.TransformNode(Name = "mono_eye")

        left_eye = avango.gua.nodes.TransformNode(Name = "left_eye")
        left_eye.Transform.value = avango.gua.make_trans_mat(-0.05, 0.0, 0.0)

        right_eye = avango.gua.nodes.TransformNode(Name = "right_eye")
        right_eye.Transform.value = avango.gua.make_trans_mat(0.05, 0.0, 0.0)


        head.Children.value = [mono_eye, left_eye, right_eye]

        screen.Children.value.append(head)
        self.EXITSCENE.Root.value.Children.value.append(screen)

    def resize_portal(self, WIDTH, HEIGHT):
        self.WIDTH  = WIDTH
        self.HEIGHT = HEIGHT
        self.ENTRYSCENE["/" + self.NAME + "Screen"].Width.value  = self.WIDTH
        self.ENTRYSCENE["/" + self.NAME + "Screen"].Height.value = self.HEIGHT
        self.GEOMETRY.Transform.value = self.sf_portal_pos.value *\
                                avango.gua.make_rot_mat(90, 1.0, 0.0, 0.0) *\
                                avango.gua.make_rot_mat(180, 0.0, 1.0, 0.0) *\
                                avango.gua.make_scale_mat(self.WIDTH, 1.0, self.HEIGHT)

    def translate_portal(self, X, Y, Z):
        self.GEOMETRY.Transform.value  = self.GEOMETRY.Transform.value * avango.gua.make_trans_mat(X, Y, Z)
        self.EXITPOS = self.EXITPOS * avango.gua.make_trans_mat(X, Y, Z)

