bl_info = {
    "name": "UV Overlapper",
    "author": "Evan Pierce",
    "version": (1, 1, 0),
    "blender": (4, 0, 0),
    "location": "UV Editor > UV > Overlap Selected Islands",
    "description": "Stacks selected UV islands so every island's origin lands at their collective center",
    "category": "UV",
}

import bpy
import bmesh
import mathutils


class UV_OT_center_selected_islands(bpy.types.Operator):
    """Move each selected UV island so all island origins overlap at their collective center"""
    bl_idname = "uv.center_selected_islands"
    bl_label = "Overlap Selected Islands"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and context.active_object.mode == 'EDIT'
        )

    def execute(self, context):
        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.verify()

        selected_faces = [f for f in bm.faces if f.select]
        if not selected_faces:
            self.report({'WARNING'}, "No faces selected")
            return {'CANCELLED'}

        # --- detect UV islands via BFS over face adjacency ---
        # Two adjacent faces are in the same island only if their shared edge
        # has matching UV coordinates on both sides (i.e. no seam).
        face_idx_set = {f.index for f in selected_faces}
        visited = set()
        islands = []

        for start in selected_faces:
            if start.index in visited:
                continue
            island = []
            stack = [start]
            visited.add(start.index)
            while stack:
                f = stack.pop()
                island.append(f)
                for loop in f.loops:
                    radial = loop.link_loop_radial_next
                    if radial is loop:
                        continue  # boundary / open edge
                    nb = radial.face
                    if nb.index in visited or nb.index not in face_idx_set:
                        continue
                    # Shared edge verts have opposite winding across the two faces:
                    #   loop.vert        == radial.link_loop_next.vert
                    #   loop.link_loop_next.vert == radial.vert
                    uv_a1 = loop[uv_layer].uv
                    uv_b1 = radial.link_loop_next[uv_layer].uv
                    uv_a2 = loop.link_loop_next[uv_layer].uv
                    uv_b2 = radial[uv_layer].uv
                    if (uv_a1 - uv_b1).length < 1e-5 and (uv_a2 - uv_b2).length < 1e-5:
                        visited.add(nb.index)
                        stack.append(nb)
            islands.append(island)

        if len(islands) < 2:
            self.report({'WARNING'}, "Need at least 2 UV islands selected")
            return {'CANCELLED'}

        # --- centroid of each island (average of all its UV coords) ---
        def island_centroid(island):
            coords = [loop[uv_layer].uv for f in island for loop in f.loops]
            return mathutils.Vector((
                sum(c.x for c in coords) / len(coords),
                sum(c.y for c in coords) / len(coords),
            ))

        centroids = [island_centroid(isl) for isl in islands]

        # --- target: average of all island centroids ---
        target = mathutils.Vector((
            sum(c.x for c in centroids) / len(centroids),
            sum(c.y for c in centroids) / len(centroids),
        ))

        # --- shift each island so its centroid lands on the target ---
        for island, centroid in zip(islands, centroids):
            offset = target - centroid
            for f in island:
                for loop in f.loops:
                    loop[uv_layer].uv += offset

        bmesh.update_edit_mesh(me)
        self.report({'INFO'}, f"Overlapped {len(islands)} UV islands at ({target.x:.4f}, {target.y:.4f})")
        return {'FINISHED'}


class UV_PT_overlapper(bpy.types.Panel):
    bl_label = "Overlapper"
    bl_idname = "UV_PT_overlapper"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Overlapper"

    def draw(self, context):
        self.layout.operator(UV_OT_center_selected_islands.bl_idname, icon='UV_SYNC_SELECT')


def menu_func(self, context):
    self.layout.operator(UV_OT_center_selected_islands.bl_idname)


def register():
    bpy.utils.register_class(UV_OT_center_selected_islands)
    bpy.utils.register_class(UV_PT_overlapper)
    bpy.types.IMAGE_MT_uvs.append(menu_func)


def unregister():
    bpy.types.IMAGE_MT_uvs.remove(menu_func)
    bpy.utils.unregister_class(UV_PT_overlapper)
    bpy.utils.unregister_class(UV_OT_center_selected_islands)
