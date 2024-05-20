bl_info = {
    "name": "Blender QFix",
    "author": "Dyvinia",
    "description": "Fix interpolation issues when importing animations from games that use SLERPed Quaternions for rotations.",
    "version": (1, 0, 1),
    "blender": (4, 0, 0),
    "category": "Animation",
}

import bpy
from bpy.types import Operator
from bpy.types import Panel
from mathutils import Quaternion

class ANIM_OT_QFix(Operator):
    """ Fixes Quaternion interpolation in current animation """
    bl_idname = "qfix.fixquat"
    bl_label = "Fix Interpolation"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.active_object.type == "ARMATURE"

    def execute(self, context):
        obj = context.object

        bone_names = [b.name for b in obj.pose.bones]
        fcurves = obj.animation_data.action.fcurves

        wm = bpy.context.window_manager
        wm.progress_begin(0, len(fcurves))

        for curve_index in range(len(fcurves)):
            curve = fcurves[curve_index]

            wm.progress_update(curve_index)

            # iterate through all the bones' fcurves' w channel
            if curve.data_path.split('"')[1] in bone_names and curve.array_index == 0 and curve.data_path.split('.')[-1] == 'rotation_quaternion':

                # w will be current index's fcurve, x is next fcurve, etc
                fqw = fcurves[curve_index]
                fqx = fcurves[curve_index + 1]
                fqy = fcurves[curve_index + 2]
                fqz = fcurves[curve_index + 3]

                # invert quaternion so that interpolation takes the shortest path
                if (len(fqw.keyframe_points) > 0):
                    fqw.keyframe_points[0].interpolation = "LINEAR"
                    fqx.keyframe_points[0].interpolation = "LINEAR"
                    fqy.keyframe_points[0].interpolation = "LINEAR"
                    fqz.keyframe_points[0].interpolation = "LINEAR"

                    for i in range(len(fqw.keyframe_points)):
                        startQuat = Quaternion((fqw.keyframe_points[i - 1].co[1],
                                                fqx.keyframe_points[i - 1].co[1],
                                                fqy.keyframe_points[i - 1].co[1],
                                                fqz.keyframe_points[i - 1].co[1]))
                        
                        endQuat = Quaternion((fqw.keyframe_points[i].co[1],
                                              fqx.keyframe_points[i].co[1],
                                              fqy.keyframe_points[i].co[1],
                                              fqz.keyframe_points[i].co[1]))
    
                        if startQuat.dot(endQuat) < 0:
                            fqw.keyframe_points[i].co[1] = -fqw.keyframe_points[i].co[1]
                            fqx.keyframe_points[i].co[1] = -fqx.keyframe_points[i].co[1]
                            fqy.keyframe_points[i].co[1] = -fqy.keyframe_points[i].co[1]
                            fqz.keyframe_points[i].co[1] = -fqz.keyframe_points[i].co[1]
    
                        
                        fqw.keyframe_points[i].interpolation = "LINEAR"
                        fqx.keyframe_points[i].interpolation = "LINEAR"
                        fqy.keyframe_points[i].interpolation = "LINEAR"
                        fqz.keyframe_points[i].interpolation = "LINEAR"

        wm.progress_end()
        
        return {'FINISHED'}

class PANEL_PT_QFix(Panel):
    bl_label = "QFix"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.active_object.type == "ARMATURE"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator("qfix.fixquat", icon='ANIM_DATA')

def register():
    bpy.utils.register_class(ANIM_OT_QFix)
    bpy.utils.register_class(PANEL_PT_QFix)


def unregister():
    bpy.utils.unregister_class(ANIM_OT_QFix)
    bpy.utils.unregister_class(PANEL_PT_QFix)