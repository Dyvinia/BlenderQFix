bl_info = {
    "name": "Blender QFix",
    "author": "Dyvinia",
    "description": "Fixes interpolation issues when importing animations from games that use SLERPed Quaternions for rotations.",
    "version": (1, 0, 8),
    "blender": (4, 0, 0),
    "category": "Animation",
}

import bpy # type: ignore
from bpy.types import Operator # type: ignore
from bpy.types import Panel # type: ignore
from mathutils import Quaternion # type: ignore

class ANIM_OT_QFix(Operator):
    """ Fixes Quaternion interpolation in current animation """
    bl_idname = "qfix.fixquat"
    bl_label = "Fix Interpolation"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.active_object and context.active_object.type == "ARMATURE"

    def execute(self, context):
        for obj in context.selected_objects:
            bone_names = [b.name for b in obj.pose.bones]
            
            if obj.animation_data:
                if obj.animation_data.action:
                    fcurves = obj.animation_data.action.fcurves
    
                    wm = bpy.context.window_manager
                    wm.progress_begin(0, len(fcurves))
    
                    fix_interpolation(fcurves, bone_names, wm)
    
                    wm.progress_end()
            
        return {'FINISHED'}
    

class ANIM_OT_QFixAll(Operator):
    """ Fixes Quaternion interpolation in current animation and all NLA strips """
    bl_idname = "qfix.fixquatall"
    bl_label = "Fix All"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.active_object and context.active_object.type == "ARMATURE"

    def execute(self, context):
        for obj in context.selected_objects:
            bone_names = [b.name for b in obj.pose.bones]
            
            if obj.animation_data:
                if obj.animation_data.action:
                    fcurves = obj.animation_data.action.fcurves
    
                    wm = bpy.context.window_manager
                    wm.progress_begin(0, len(fcurves))
    
                    fix_interpolation(fcurves, bone_names, wm)
    
                    wm.progress_end()
    
                for track in obj.animation_data.nla_tracks:
                    for strip in track.strips:
                        fcurves = strip.action.fcurves
                        
                        wm = bpy.context.window_manager
                        wm.progress_begin(0, len(fcurves))
    
                        fix_interpolation(fcurves, bone_names, wm)
    
                        wm.progress_end()
            
        return {'FINISHED'}
    

class ANIM_OT_Slerp(Operator):
    """ Applies inbetween keyframes that are SLERPed in current animation """
    bl_idname = "qfix.slerp"
    bl_label = "SLERP Inbetween"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.active_object and context.active_object.type == "ARMATURE"

    def execute(self, context):
        for obj in context.selected_objects:
            bone_names = [b.name for b in obj.pose.bones]
            
            if obj.animation_data:
                if obj.animation_data.action:
                    fcurves = obj.animation_data.action.fcurves
    
                    wm = bpy.context.window_manager
                    wm.progress_begin(0, len(fcurves))
    
                    slerp_rotations(fcurves, bone_names, wm)
    
                    wm.progress_end()
            
        return {'FINISHED'}

class ANIM_OT_SlerpAll(Operator):
    """ Applies inbetween keyframes that are SLERPed in current animation and all NLA strips """
    bl_idname = "qfix.slerpall"
    bl_label = "SLERP Inbetween All"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.active_object and context.active_object.type == "ARMATURE"

    def execute(self, context):
        for obj in context.selected_objects:
            bone_names = [b.name for b in obj.pose.bones]
            
            if obj.animation_data:
                if obj.animation_data.action:
                    fcurves = obj.animation_data.action.fcurves
    
                    wm = bpy.context.window_manager
                    wm.progress_begin(0, len(fcurves))
    
                    slerp_rotations(fcurves, bone_names, wm)
    
                    wm.progress_end()
    
                for track in obj.animation_data.nla_tracks:
                    for strip in track.strips:
                        fcurves = strip.action.fcurves
                        
                        wm = bpy.context.window_manager
                        wm.progress_begin(0, len(fcurves))
    
                        slerp_rotations(fcurves, bone_names, wm)
    
                        wm.progress_end()
            
        return {'FINISHED'}
    
def fix_interpolation(fcurves, bone_names, wm):
    for curve_index in range(len(fcurves)):
        curve = fcurves[curve_index]
            
        # only bone keyframes
        if '.' not in curve.data_path:
            continue

        # iterate through all the bones' fcurves' w channel
        if curve.data_path.split('"')[1] in bone_names and curve.array_index == 0 and curve.data_path.split('.')[-1] == 'rotation_quaternion':
            # w will be current index's fcurve, x is next fcurve, etc
            fqw = fcurves[curve_index]
            fqx = fcurves[curve_index + 1]
            fqy = fcurves[curve_index + 2]
            fqz = fcurves[curve_index + 3]

            # invert quaternion so that interpolation takes the shortest path
            endQuat = 0
            if (len(fqw.keyframe_points) > 0):
                endQuat = Quaternion((fqw.keyframe_points[0].co[1],
                                      fqx.keyframe_points[0].co[1],
                                      fqy.keyframe_points[0].co[1],
                                      fqz.keyframe_points[0].co[1]))
                
                fqw.keyframe_points[0].interpolation = "LINEAR"
                fqx.keyframe_points[0].interpolation = "LINEAR"
                fqy.keyframe_points[0].interpolation = "LINEAR"
                fqz.keyframe_points[0].interpolation = "LINEAR"

                for i in range(len(fqw.keyframe_points)):
                    startQuat = endQuat
                    endQuat = Quaternion((fqw.keyframe_points[i].co[1],
                                          fqx.keyframe_points[i].co[1],
                                          fqy.keyframe_points[i].co[1],
                                          fqz.keyframe_points[i].co[1]))
    
                    if startQuat.dot(endQuat) < 0:
                        endQuat.negate()
                        fqw.keyframe_points[i].co[1] = -fqw.keyframe_points[i].co[1]
                        fqx.keyframe_points[i].co[1] = -fqx.keyframe_points[i].co[1]
                        fqy.keyframe_points[i].co[1] = -fqy.keyframe_points[i].co[1]
                        fqz.keyframe_points[i].co[1] = -fqz.keyframe_points[i].co[1]
                    
                    fqw.keyframe_points[i].interpolation = "LINEAR"
                    fqx.keyframe_points[i].interpolation = "LINEAR"
                    fqy.keyframe_points[i].interpolation = "LINEAR"
                    fqz.keyframe_points[i].interpolation = "LINEAR"
                    
        wm.progress_update(curve_index)
        
def slerp_rotations(fcurves, bone_names, wm):
    for curve_index in range(len(fcurves)):
        curve = fcurves[curve_index]
            
        # only bone keyframes
        if '.' not in curve.data_path:
            continue
        
        if curve.data_path.split('"')[1] in bone_names and curve.array_index == 0 and curve.data_path.split('.')[-1] == 'rotation_quaternion':
            # w will be current index's fcurve, x is next fcurve, etc
            fqw = fcurves[curve_index]
            fqx = fcurves[curve_index + 1]
            fqy = fcurves[curve_index + 2]
            fqz = fcurves[curve_index + 3]

            if (len(fqw.keyframe_points) > 0):
                current = 0
                for i in range(len(fqw.keyframe_points)):
                    if current + 1 >= len(fqw.keyframe_points):
                        continue
                    
                    startQuat = Quaternion((fqw.keyframe_points[current].co[1],
                                            fqx.keyframe_points[current].co[1],
                                            fqy.keyframe_points[current].co[1],
                                            fqz.keyframe_points[current].co[1]))
                    startFrame = fqw.keyframe_points[current].co[0]
                    
                    endQuat = Quaternion((fqw.keyframe_points[current+1].co[1],
                                          fqx.keyframe_points[current+1].co[1],
                                          fqy.keyframe_points[current+1].co[1],
                                          fqz.keyframe_points[current+1].co[1]))
                    endFrame = fqw.keyframe_points[current+1].co[0]
                    
                    midQuat = startQuat.slerp(endQuat, 0.5)
                    midFrame = (startFrame + endFrame) / 2
                    
                    fqw.keyframe_points.insert(midFrame, midQuat.w)
                    fqx.keyframe_points.insert(midFrame, midQuat.x)
                    fqy.keyframe_points.insert(midFrame, midQuat.y)
                    fqz.keyframe_points.insert(midFrame, midQuat.z)
                    
                    current += 2
                    
        wm.progress_update(curve_index)

class PANEL_PT_QFix(Panel):
    bl_label = "QFix"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.active_object and context.active_object.type == "ARMATURE"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator("qfix.fixquat", icon='ANIM_DATA')
        col.operator("qfix.fixquatall", icon='ANIM_DATA')
        
        col = self.layout.column(align=True)
        col.operator("qfix.slerp", icon='ANIM_DATA')
        col.operator("qfix.slerpall", icon='ANIM_DATA')

def register():
    bpy.utils.register_class(ANIM_OT_QFix)
    bpy.utils.register_class(ANIM_OT_QFixAll)
    bpy.utils.register_class(ANIM_OT_Slerp)
    bpy.utils.register_class(ANIM_OT_SlerpAll)
    bpy.utils.register_class(PANEL_PT_QFix)


def unregister():
    bpy.utils.unregister_class(ANIM_OT_QFix)
    bpy.utils.unregister_class(ANIM_OT_QFixAll)
    bpy.utils.unregister_class(ANIM_OT_Slerp)
    bpy.utils.unregister_class(ANIM_OT_SlerpAll)
    bpy.utils.unregister_class(PANEL_PT_QFix)