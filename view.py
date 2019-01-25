from open3d import *

pcd = read_point_cloud("output.ply")
draw_geometries([pcd])