import bpy

def main():
    def sort_collection(collection, case = False):
        if collection.children is None: return
        children = sorted (
            collection.children, 
            key = lambda c: c.name if case else c.name.lower()
            )
        for child in children:
            viewportVisibility_before = child.hide_viewport
            renderVisibility_before = child.hide_render
            collection.children.unlink(child)
            collection.children.link(child)
            child.hide_viewport = viewportVisibility_before
            child.hide_render = renderVisibility_before
            sort_collection(child)
    # case_sensitive sort, (default is False)
    case_sensitive = True
    for scene in bpy.data.scenes:
        sort_collection(scene.collection, case_sensitive)

class AlphabetizeOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.alphabetize"
    bl_label = "Alphabetize Collections & Objects"

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        main()
        return {'FINISHED'}

class AlphabetizePanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "AlphabetizePanel"
    bl_idname = "SCENE_PT_alphabetize"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Big render button
        layout.label(text="Alphabetize")
        row = layout.row()
        row.scale_y = 2.0
        row.operator("object.alphabetize")

def register():
    bpy.utils.register_class(AlphabetizeOperator)
    bpy.utils.register_class(AlphabetizePanel)

def unregister():
    bpy.utils.unregister_class(AlphabetizePanel)
    bpy.utils.unregister_class(AlphabetizeOperator)

if __name__ == "__main__":
    register()
