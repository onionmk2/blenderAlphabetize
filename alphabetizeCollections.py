bl_info = {
        "name": "Alphabetize",
        "author": "Philip Leclerc",
        "version": (1, 0),
        "blender": (2, 80, 0),
        "location": "Scene > Alphabetize",
        "description": "Alphabetizes collections & objects, preserving viewport/render visibility.",
        "warning": "",
        "wiki_url": "",
        "category": "",
}

import bpy

def getLayerCollection(layerCollection, collectionName):
    """
        As 0f 2.80, needed to acquire a layer collection corresponding to a target collection: https://blender.stackexchange.com/a/127700/73773
    """
    found = None
    if (layerCollection.name == collectionName):
        return layerCollection
    for layer in layerCollection.children:
        found = getLayerCollection(layer, collectionName)
        if found:
            return found

def sort_collection(collection, case = False):
    """
        Recursively sorts collections & objects alphabetically: https://blender.stackexchange.com/a/159897/73773

        Minor modifications to BSE answer made to preserve viewport/render visibility before/after collection unlinking

        Substantial modifications later made to switch from using Disable in Viewports to using Hide in Viewport. See:
            https://blender.stackexchange.com/a/155605/73773y
    """
    if collection.children is None: return
    children = sorted (
        collection.children, 
        key = lambda c: c.name if case else c.name.lower()
        )
    for child in children:
        print("Alphabetizing child " + child.name)
        objViewportVisibility_before, objRenderVisibility_before = {}, {}
        if type(child) is bpy.types.Collection: # Use view layer to access local/'temporary' hide_viewport
            childLayerCollection = getLayerCollection(bpy.context.view_layer.layer_collection, child.name)
            bpy.context.view_layer.active_layer_collection = childLayerCollection
            viewportVisibility_before = bpy.context.view_layer.active_layer_collection.hide_viewport
            renderVisibility_before = bpy.context.view_layer.active_layer_collection.collection.hide_render
            for obj in child.objects: # Use hide_get()/hide_set(bool) to access local/'temporary' hide_viewport
                objViewportVisibility_before[obj.name] = obj.hide_get()
                objRenderVisibility_before[obj.name] = obj.hide_render
        else:
            print("WARNING: Found child of type " + str(type(child)) + ". Doing nothing to it.")

        collection.children.unlink(child)
        collection.children.link(child)

        if type(child) is bpy.types.Collection: # Use view layer to access local/'temporary' hide_viewport
            childLayerCollection = getLayerCollection(bpy.context.view_layer.layer_collection, child.name) # Necessary to do twice?
            bpy.context.view_layer.active_layer_collection = childLayerCollection
            print("Setting coll child " + child.name + " hide-visibility to " + str(viewportVisibility_before))
            bpy.context.view_layer.active_layer_collection.hide_viewport = viewportVisibility_before
            bpy.context.view_layer.active_layer_collection.collection.hide_render = renderVisibility_before
            for obj in child.objects: # Use hide_get()/hide_set(bool) to access local/'temporary' hide_viewport
                print("Setting obj " + obj.name + " hide-visibility to " + str(objViewportVisibility_before[obj.name]))
                obj.hide_set(objViewportVisibility_before[obj.name])
                obj.hide_render = objRenderVisibility_before[obj.name]
        else:
            print("WARNING: Found child of type " + str(type(child)) + ". Doing nothing to it.")

        sort_collection(child)

# Main alphabetize function
def main():
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
        print("\n\n\n\n ================== Beginning alphabetize ==================")
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
