import os
import time
import torch
from torch.autograd import Variable
from torchvision import datasets, transforms
import scipy.io
import warnings
warnings.filterwarnings("ignore")
import scipy.misc
#from PIL import Image

from darknet import Darknet
import dataset
from utils import *
from MeshPly import MeshPly

main_path = "./custom"
model_name = ["block_tower", "block_A", "block_B", "block_C", "block_D", "block_E"]
edges_corners = [[0, 1], [0, 2], [0, 4], [1, 3], [1, 5], [2, 3], [2, 6], [3, 7], [4, 5], [4, 6], [5, 7], [6, 7]]
intrinsic_calibration = get_camera_intrinsic(320, 240, 640, 658.8)
im_width     = 640
im_height    = 480

# Create new directory
def makedirs(path):
    if not os.path.exists( path ):
        os.makedirs( path )

def distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 + (pos1[2] - pos2[2])**2)

all_3d_position_points = []
all_2d_position_points = []
colors = ["b", "m", "g", "y", "c", "r" ]

if __name__ == '__main__':
    for i in model_name:
        datacfg = 'custom/' + i + '/' + i + '.data'
        modelcfg = 'cfg/yolo-pose.cfg'
        weightfile = 'backup/' + i + '/model.weights'
        
        data_options = read_data_cfg(datacfg)
        valid_images = data_options['valid']
        backupdir    = data_options['backup']
        name         = data_options['name']
        gpus         = data_options['gpus'] 
        meshname     = data_options['mesh']
        mesh      = MeshPly(meshname)
        vertices  = np.c_[np.array(mesh.vertices), np.ones((len(mesh.vertices), 1))].transpose()
        corners3D = get_3D_corners(vertices)
        diam = float(data_options['diam'])
        diam_real  = float(data_options['diam_real'])
        
        with open(valid_images) as fp:
            tmp_files = fp.readlines()
            valid_files = [item.rstrip() for item in tmp_files]

        preds_corners2D     = []
        model = Darknet(modelcfg)
        model.load_weights(weightfile)
        model.cuda()
        model.eval()
        test_width    = model.test_width
        test_height   = model.test_height
        num_keypoints = model.num_keypoints 
        num_labels    = num_keypoints * 2 + 3

        valid_dataset = dataset.listDataset(valid_images, 
                                            shape=(test_width, test_height),
                                            shuffle=False,
                                            transform=transforms.Compose([transforms.ToTensor(),]))

        kwargs = {'num_workers': 4, 'pin_memory': True}
        test_loader = torch.utils.data.DataLoader(valid_dataset, batch_size=1, shuffle=False, **kwargs) 

        logging("   Testing {}...".format(name))
        logging("   Number of test samples: %d" % len(test_loader.dataset))
        for batch_idx, (data, target) in enumerate(test_loader):
            img = data[0, :, :, :]
            img = img.numpy().squeeze()
            img = np.transpose(img, (1, 2, 0))
            data = data.cuda()
            target = target.cuda()
            data = Variable(data, volatile=True)
            output = model(data).data  
            all_boxes = get_region_boxes(output, 1, num_keypoints)        
            for box_pr, target in zip([all_boxes], [target[0]]):
                corners2D_pr = np.array(np.reshape(box_pr[:18], [9, 2]), dtype='float32')         
                corners2D_pr[:, 0] = corners2D_pr[:, 0] * im_width
                corners2D_pr[:, 1] = corners2D_pr[:, 1] * im_height
                preds_corners2D.append(corners2D_pr)
                R_pr, t_pr = pnp(np.array(np.transpose(np.concatenate((np.zeros((3, 1)), corners3D[:3, :]), axis=1)), dtype='float32'),  corners2D_pr, np.array(intrinsic_calibration, dtype='float32'))
                Rt_pr        = np.concatenate((R_pr, t_pr), axis=1)
                camera_trans = compute_transformation(corners3D, Rt_pr)
                camera_trans[1,:] = -camera_trans[1,:]
                all_3d_position_points.append(camera_trans)
                camera_projection = intrinsic_calibration.dot(camera_trans)
                projections_2d = np.zeros((2, corners3D.shape[1]), dtype='float32')
                projections_2d[0, :] = camera_projection[0, :]/camera_projection[2, :]
                projections_2d[1, :] = camera_projection[1, :]/camera_projection[2, :]
                proj_corners_pr = np.transpose(projections_2d)
                all_2d_position_points.append(proj_corners_pr)


    #img = Image.open(os.path.join(main_path, "save.jpg"), mode='r', formats=None)
    result_string = ""
    '''
    plt.xlim((0, im_width))
    plt.ylim((0, im_height))
    plt.imshow(scipy.misc.imresize(img, (im_height, im_width)))'''
    for i in range(6):
        result_string += np.array2string(all_3d_position_points[i], formatter={'float_kind':lambda x: "%.5f" % x}) + "\n"
        '''for edge in edges_corners:
            #plt.plot([corners2D_pr[edge[0] + 1][0], corners2D_pr[edge[1] + 1][0]], [corners2D_pr[edge[0] + 1][1], corners2D_pr[edge[1] + 1][1]], color='g', linewidth=2.0)
            plt.plot(all_2d_position_points[i][edge, 0], 480-all_2d_position_points[i][edge, 1], color=colors[i], linewidth=3.0)
            '''
    #plt.gca().invert_yaxis()
    #plt.savefig(main_path + "\\result.jpg", dpi=150)'''
    result_text = open(os.path.join(main_path, "result.txt"),"w")
    result_text.write(result_string)
    result_text.close()