#!/usr/bin/python

## @file
# Contains class User.

# import guacamole libraries
import avango
import avango.gua

# import portal libraries
from portal_lib.PortalController import *  

# import interface libraries
from interface_lib.Manipulator import *

# import python libraries
import math
import random

## Base class to represent attributes and functions that all users have in common. Not to be instantiated.

class User:
  
  # output fields
  ## @var sf_abs_head_mat
  # Position and rotation of the user's head with respect to the platform.
  sf_abs_head_mat = avango.gua.SFMatrix4()
  sf_abs_head_mat = avango.gua.make_identity_mat()

  # pipeline values to be used
  ## @var enable_bloom
  # Boolean variable to enable bloom on all pipelines.
  enable_bloom = True

  ## @var bloom_intensity
  # Bloom intensity value for all pipelines.
  bloom_intensity = 0.1

  ## @var bloom_threshold
  # Bloom threshold value for all pipelines.
  bloom_threshold = 1.0

  ## @var bloom_radius
  # Bloom radius value for all pipelines.
  bloom_radius = 10

  ## @var enable_fxaa
  # Boolean variable to enable FXAA on all pipelines.
  enable_fxaa = False

  ## @var enable_fog
  # Boolean variable to enable fog on all pipelines.
  enable_fog = True

  ## @var fog_start
  # Fog starting distance for all pipelines.
  fog_start = 300.0

  ## @var fog_end
  # Fog ending distance for all pipelines.
  fog_end = 400.0

  ## @var enable_frustum_culling
  # Boolean variable to enable frustum culling on all pipelines.
  enable_frustum_culling = False

  ## @var ambient_color
  # Ambient color value for all pipelines.
  ambient_color = avango.gua.Color(0.5, 0.5, 0.5)

  ## @var far_clip
  # Distance of the far clipping plane for all pipelines.
  far_clip = 800.0

  ## @var enable_backface_culling
  # Boolean variable to enable backface culling on all pipelines.
  enable_backface_culling = False

  ## @var enable_ssao
  # Boolean variable to enable Ssao on all pipelines.
  enable_ssao = True

  ## @var ssao_radius
  # Ssao radius value for all pipelines.
  ssao_radius = 2.0

  ## @var ssao_intensity
  # Ssao intensity value for all pipelines.
  ssao_intensity = 2.0

  ## @var enable_ssao
  # Boolean variable to enable FPS display on all pipelines.
  enable_fps_display = True

  # static class variables
  ## @var avatar_materials
  # List of materials to choose from when an avatar is created.
  avatar_materials = ['AvatarBlue', 'AvatarCyan', 'AvatarGreen', 'AvatarMagenta',
                      'AvatarOrange', 'AvatarRed', 'AvatarWhite', 'AvatarYellow']

  ## @var material_used
  # List of booleans to indicate if a material in avatar_materials was already used.
  material_used = [False, False, False, False,
                   False, False, False, False]

  ## Custom constructor.
  # @param NODE_PRETEXT The prefix to be used when creating scenegraph nodes.
  def __init__(self, NODE_PRETEXT):

    ## @var node_pretext
    # Prefix of the scenegraph nodes this user creates.
    self.node_pretext = NODE_PRETEXT

    ## @var portal_controller
    # coordinates interaction with portals in the scene
    self.portal_controller = PortalController()


  ## Sets the transformation values of left and right eye.
  # @param VALUE The eye distance to be applied.
  def set_eye_distance(self, VALUE):
    self.left_eye.Transform.value  = avango.gua.make_trans_mat(VALUE * -0.5, 0.0, 0.0)
    self.right_eye.Transform.value = avango.gua.make_trans_mat(VALUE * 0.5, 0.0, 0.0)

  ## Sets all the pipeline values to the ones specified in User class.
  def set_pipeline_values(self):
    self.pipeline.EnableBloom.value             = self.enable_bloom
    self.pipeline.BloomIntensity.value          = self.bloom_intensity
    self.pipeline.BloomThreshold.value          = self.bloom_threshold
    self.pipeline.BloomRadius.value             = self.bloom_radius
    self.pipeline.EnableFXAA.value              = self.enable_fxaa
    self.pipeline.EnableFog.value               = self.enable_fog
    self.pipeline.FogStart.value                = self.fog_start
    self.pipeline.FogEnd.value                  = self.fog_end
    self.pipeline.EnableFrustumCulling.value    = self.enable_frustum_culling
    self.pipeline.AmbientColor.value            = self.ambient_color
    self.pipeline.FarClip.value                 = self.far_clip
    self.pipeline.EnableBackfaceCulling.value   = self.enable_backface_culling
    self.pipeline.EnableSsao.value              = self.enable_ssao
    self.pipeline.SsaoRadius.value              = self.ssao_radius
    self.pipeline.SsaoIntensity.value           = self.ssao_intensity
    self.pipeline.EnableFPSDisplay.value        = self.enable_fps_display
    self.pipeline.FogTexture.value              = self.pipeline.BackgroundTexture.value
   # self.pipeline.EnableRayDisplay.value        = True

  ## Appends a node to the children of a platform in the scenegraph.
  # @param SCENEGRAPH Reference to the scenegraph.
  # @param PLATFORM_ID The id of the platform to append the node to.
  # @param NODE The node to be appended to the platform node.
  def append_to_platform(self, SCENEGRAPH, PLATFORM_ID, NODE):
    SCENEGRAPH['/platform_' + str(PLATFORM_ID)].Children.value.append(NODE)
    self.portal_controller.PLATFORM = PLATFORM_ID
    self.portal_controller.ACTIVESCENE = SCENEGRAPH
     

  ## Creates a basic avatar for this user.
  # @param SCENEGRAPH Reference to the scenegraph.
  # @param PLATFORM_ID The id of the platform to append the avatar to.
  # @param SF_AVATAR_BODY_MATRIX Field containing the transformation matrix for the avatar's body on the platform.
  def create_avatar_representation(self, SCENEGRAPH, PLATFORM_ID, SF_AVATAR_BODY_MATRIX, LEFTHAND_MAT, RIGHTHAND_MAT):
    _loader = avango.gua.nodes.GeometryLoader()

    # if every material has already been used, reset the pool
    _reset_pool = True

    for _boolean in User.material_used:
      if _boolean == False:
        _reset_pool = False
        break

    if _reset_pool:
      User.material_used = [False, False, False, False, False, False, False, False]

    # get a random material from the pool of materials
    _random_material_number = random.randint(0, len(User.avatar_materials) - 1)
 
    # if the material is already used, go further until the first unused one is found
    while User.material_used[_random_material_number] == True:
      _random_material_number = (_random_material_number + 1) % len(User.material_used)

    # get the selected material 
    _material = User.avatar_materials[_random_material_number]
    User.material_used[_random_material_number] = True
    
    # create avatar head
    ## @var head_avatar
    # Scenegraph node representing the geometry and transformation of the basic avatar's head.
    self.head_avatar = _loader.create_geometry_from_file( self.node_pretext + '_head_avatar_' + str(PLATFORM_ID),
                                                          'data/objects/default_avatar_head.obj',
                                                          _material,
                                                          avango.gua.LoaderFlags.LOAD_MATERIALS)
    self.head_avatar.Transform.value = avango.gua.make_rot_mat(90, 0, 1, 0) * avango.gua.make_scale_mat(0.2, 0.2, 0.2)
    self.head_avatar.GroupNames.value = [self.node_pretext + '_avatar_group_' + str(PLATFORM_ID)]
    self.head_transform.Children.value.append(self.head_avatar)

    # create avatar body
    ## @var body_avatar
    # Scenegraph node representing the geometry and transformation of the basic avatar's body.
    self.body_avatar = _loader.create_geometry_from_file( self.node_pretext + '_body_avatar_' + str(PLATFORM_ID),
                                                          'data/objects/default_avatar_body.obj',
                                                          _material,
                                                          avango.gua.LoaderFlags.LOAD_MATERIALS)
    self.body_avatar.GroupNames.value = [self.node_pretext + '_avatar_group_' + str(PLATFORM_ID)]
    SCENEGRAPH['/platform_' + str(PLATFORM_ID)].Children.value.append(self.body_avatar)

    self.body_avatar.Transform.connect_from(SF_AVATAR_BODY_MATRIX)

    # create hands for the avatar
    # left hand
    self.left_hand_avatar = _loader.create_geometry_from_file( self.node_pretext + '_left_hand_avatar_' + str(PLATFORM_ID),
                                                          'data/objects/hand.obj',
                                                          _material,
                                                          avango.gua.LoaderFlags.LOAD_MATERIALS)

    self.left_hand_transform = avango.gua.nodes.TransformNode(Name = self.node_pretext + '_left_hand_transform_' + str(PLATFORM_ID))
    self.left_hand_transform.Children.value.append(self.left_hand_avatar)
    SCENEGRAPH['/platform_' + str(PLATFORM_ID)].Children.value.append(self.left_hand_transform)


    # right hand
    self.right_hand_avatar = _loader.create_geometry_from_file( self.node_pretext + '_right_hand_avatar_' + str(PLATFORM_ID),
                                                          'data/objects/hand.obj',
                                                          _material,
                                                          avango.gua.LoaderFlags.LOAD_MATERIALS)

    self.right_hand_transform = avango.gua.nodes.TransformNode(Name = self.node_pretext + '_right_hand_transform_' + str(PLATFORM_ID))
    self.right_hand_transform.Children.value.append(self.right_hand_avatar)
    SCENEGRAPH['/platform_' + str(PLATFORM_ID)].Children.value.append(self.right_hand_transform)


    # OVR User and PowerwallUser get 'Pointer-Hands'
    if self.node_pretext == "ovr" or self.node_pretext == "powerwall": # ! powerwall pretext richtig???
      # Left Hand
      self.left_hand_avatar.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, 0.15) * avango.gua.make_scale_mat(2.0, 2.0, 2.0)  
      self.left_hand_transform.Transform.connect_from(LEFTHAND_MAT)

      # Right Hand
      self.right_hand_avatar.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, 0.15) * avango.gua.make_scale_mat(2.0, 2.0, 2.0)
      self.right_hand_transform.Transform.connect_from(RIGHTHAND_MAT)




    # create desktop user table and default hands
    if self.node_pretext == "desktop":
      # Left Hand
      self.left_hand_avatar.Transform.value = avango.gua.make_trans_mat(-0.2, 0.8, 1.3) * avango.gua.make_scale_mat(2.0, 2.0, 2.0)

      # Right Hand
      self.right_hand_avatar.Transform.value = avango.gua.make_trans_mat(0.2, 0.8, 1.3) * avango.gua.make_scale_mat(2.0, 2.0, 2.0)

      ## @var table_transform
      # Scenegraph transform node for the dekstop user's table.
      self.table_transform = avango.gua.nodes.TransformNode(Name = 'table_transform')
      self.table_transform.Transform.value = avango.gua.make_trans_mat(0, -0.5, -3)
      self.body_avatar.Children.value.append(self.table_transform)

      ## @var table_avatar
      # Scenegraph node representing the geometry and transformation of the desktop user's table.
      self.table_avatar = _loader.create_geometry_from_file( self.node_pretext + '_desktop_avatar_' + str(PLATFORM_ID),
                                                             'data/objects/cube.obj',
                                                             _material,
                                                             avango.gua.LoaderFlags.LOAD_MATERIALS)
      self.table_avatar.Transform.value =  avango.gua.make_scale_mat(3.0, 0.5, 1.0)
      self.table_transform.Children.value.append(self.table_avatar)
      self.table_avatar.GroupNames.value = [self.node_pretext + '_avatar_group_' + str(PLATFORM_ID)]
