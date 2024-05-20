bl_info = {
    "name": "Blender QFix",
    "author": "Dyvinia",
    "description": "Fix interpolation issues when importing quarternion animations ",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "category": "Animation",
}

import bpy
from bpy.types import Operator
from bpy.types import Panel
from mathutils import Quaternion

class ANIM_OT_QFix(Operator):
    """ Fix Quarternion Interpolation Issues """
    bl_idname = "qfix.fixquart"
    bl_label = "Fix Interpolation"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.active_object.type == 'ARMATURE'

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
                fqx = fcurves[curve_index+1]
                fqy = fcurves[curve_index+2]
                fqz = fcurves[curve_index+3]

                #print(fqw.data_path + str(fqw.array_index))
                #print(fqx.data_path + str(fqx.array_index))
                #print(fqy.data_path + str(fqy.array_index))
                #print(fqz.data_path + str(fqz.array_index))

                # invert quaternion so that interpolation takes the shortest path
                endQuat = 0
                if (len(fqw.keyframe_points) > 0):
                    endQuat = Quaternion((fqw.keyframe_points[0].co[1],fqx.keyframe_points[0].co[1],fqy.keyframe_points[0].co[1],fqz.keyframe_points[0].co[1] ))

                    fqw.keyframe_points[0].interpolation = "LINEAR"
                    fqx.keyframe_points[0].interpolation = "LINEAR"
                    fqy.keyframe_points[0].interpolation = "LINEAR"
                    fqz.keyframe_points[0].interpolation = "LINEAR"

                    for i in range(len(fqw.keyframe_points) - 1):
                        startQuat = endQuat
                        endQuat = Quaternion((fqw.keyframe_points[i+1].co[1],fqx.keyframe_points[i+1].co[1],fqy.keyframe_points[i+1].co[1],fqz.keyframe_points[i+1].co[1] ))
    
                        if startQuat.dot(endQuat) < 0:
                            endQuat.negate()
                            fqw.keyframe_points[i+1].co[1] = -fqw.keyframe_points[i+1].co[1]
                            fqx.keyframe_points[i+1].co[1] = -fqx.keyframe_points[i+1].co[1]
                            fqy.keyframe_points[i+1].co[1] = -fqy.keyframe_points[i+1].co[1]
                            fqz.keyframe_points[i+1].co[1] = -fqz.keyframe_points[i+1].co[1]
    
                        
                        fqw.keyframe_points[i+1].interpolation = "LINEAR"
                        fqx.keyframe_points[i+1].interpolation = "LINEAR"
                        fqy.keyframe_points[i+1].interpolation = "LINEAR"
                        fqz.keyframe_points[i+1].interpolation = "LINEAR"

        wm.progress_end()
        
        return {'FINISHED'}

class PANEL_PT_QFix(Panel):
    bl_label = "QFix"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.active_object.type == 'ARMATURE'

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator("qfix.fixquart", icon='ANIM_DATA')

def register():
    bpy.utils.register_class(ANIM_OT_QFix)
    bpy.utils.register_class(PANEL_PT_QFix)


def unregister():
    bpy.utils.unregister_class(ANIM_OT_QFix)
    bpy.utils.unregister_class(PANEL_PT_QFix)