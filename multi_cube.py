from vispy.geometry import create_box
import vispy.scene
import vispy.visuals
from itertools import repeat
import numpy as np
import multiprocessing as mp
from functools import partial

def gen_job(i: int, offset: int, positions: list[tuple[3]], vertex_colors: list | None, face_colors: list | None,
            size, width_segments, height_segments, depth_segments, planes):
    vertex_itr = None
    vertices = []
    filled_indices = []
    outline_indices = []
    all_face_colors = []
    all_vertex_colors = []

    start = int(offset * i)
    end = int(offset * (i + 1))

    maxIndex = 0 if start == 0 else 24 * (int(offset * i) - int(0))
    if(vertex_colors is None):
        vertex_itr = repeat(vertex_colors)
    else:
        vertex_itr = vertex_colors[start:end].copy()

    face_colors_itr = None
    if(face_colors is None):
        face_colors_itr = repeat(face_colors)
    else:
        face_colors_itr = face_colors[start:end].copy()

    for position, vertex_color, face_color in zip(positions[start:end], vertex_itr, face_colors_itr):
        box_vertices, box_filled_indices, box_outline_indices = create_box(
            size, size, size, width_segments, height_segments,
            depth_segments, planes)
        
        for column, pos in zip(box_vertices['position'].T, position):
            column += pos
        
        box_filled_indices += maxIndex
        box_outline_indices += maxIndex
        vertexNumber = len(box_vertices)
        maxIndex += vertexNumber

        vertices.append(box_vertices)
        filled_indices.append(box_filled_indices)
        outline_indices.append(box_outline_indices)
        
        if vertex_color is not None:
            all_vertex_colors.extend([vertex_color] * vertexNumber)
        if face_color is not None:
            all_face_colors.extend([face_color] * len(box_filled_indices))

    return (vertices, filled_indices, outline_indices, all_vertex_colors, all_face_colors)

class MultiCubeVisual(vispy.visuals.BoxVisual):
    def __init__(self, size=1, positions=[(0, 0, 0)], width_segments=1,
                 height_segments=1, depth_segments=1, planes=None,
                 vertex_colors=None, face_colors=None,
                 color=(0.5, 0.5, 1, 0.5), edge_color=None, **kwargs):
        self._mesh = None
        self._border = None
        
        self.set_data(size=size, positions=positions, width_segments=width_segments, height_segments=height_segments,
                       depth_segments=depth_segments,
                      planes=planes, vertex_colors=vertex_colors, face_colors=face_colors, color=color,
                      edge_color=edge_color)

        vispy.visuals.CompoundVisual.__init__(self, [self._mesh, self._border], **kwargs)
        self.mesh.set_gl_state(polygon_offset_fill=True,
                               polygon_offset=(1, 1), depth_test=True)
        
    def set_data(self, size=1, positions=[(0, 0, 0)], width_segments=1,
            height_segments=1, depth_segments=1, planes=None,
            vertex_colors=None, face_colors=None,
            color=(0.5, 0.5, 1, 0.5), edge_color=None):
        
        vertices = []
        filled_indices = []
        outline_indices = []
        all_vertex_colors = []
        all_face_colors = []
        
        if vertex_colors is None:
            all_vertex_colors = None
        
        if face_colors is None:
            all_face_colors = None
        offset = len(positions) / mp.cpu_count()
        with mp.Pool(processes=mp.cpu_count()) as pool:
            arg = partial(gen_job,
                    positions=positions, vertex_colors=vertex_colors, face_colors=face_colors,
                    size=size, width_segments=width_segments, height_segments=height_segments, depth_segments=depth_segments, planes=planes)
    
            results = pool.starmap(arg, tuple([(x, offset) for x in range(mp.cpu_count())]))
            for i in range(len(results)):
                    vertices.extend(results[i][0])
                    filled_indices.extend(results[i][1])
                    outline_indices.extend(results[i][2])
                    if(all_vertex_colors is not None and results[i][3] is not None):
                        all_vertex_colors.extend(results[i][3])

                    if(all_face_colors is not None and results[i][4] is not None):
                        all_face_colors.extend(results[i][4])

        vertices = np.concatenate(vertices)
        filled_indices = np.vstack(filled_indices)
        outline_indices = np.vstack(outline_indices)
        if(self._mesh is None):
            self._mesh = vispy.visuals.MeshVisual(vertices['position'], filled_indices,
                                    all_vertex_colors, all_face_colors, color)
        else:
            self._mesh.set_data(vertices['position'], filled_indices,
                                all_vertex_colors, all_face_colors, color)
        
        if(self._border is None):
            if edge_color:
                self._border = vispy.visuals.MeshVisual(vertices['position'], outline_indices,
                                      color=edge_color, mode='lines')
            else:
                self._border = vispy.visuals.MeshVisual()
        else:
            if edge_color:
                self._border.set_data(vertices['position'], outline_indices,
                                        color=edge_color)

MultiCube = vispy.scene.visuals.create_visual_node(MultiCubeVisual)
