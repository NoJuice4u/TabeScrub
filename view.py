from open3d import *

pcd = read_point_cloud("data\\output.ply")
draw_geometries([pcd])