from sensor_msgs.msg import PointCloud2
from path_interface.srv import Path
import rclpy
from rclpy.node import Node
import csv
import numpy as np
import pathlib
import argparse
parser = argparse.ArgumentParser(description='Choose topic to subscribe to')
    
    # Add arguments
parser.add_argument('--input_topic', type=str, default='/lidar_points')

    # We must use parse_known_args() because ROS 2 adds its own arguments 
    # (like __node:=...) which argparse would otherwise treat as errors.
args, unknown = parser.parse_known_args()
class LagLogger(Node):
    def __init__(self,input_topic):
        super().__init__('lag_logger')
        self.subscription = self.create_subscription(PointCloud2, input_topic, self.listener_callback, 10)
        self.lag_list=[]
        self.srv = self.create_service(Path, 'dump_lags', self.dump_lags_callback)
    def listener_callback(self,msg : PointCloud2):
        now=self.get_clock().now()
        msg_time=rclpy.time.Time.from_msg(msg.header.stamp)
        print("Lag logger node clock type: "+str(now.clock_type))
        print("Hesai clock type: "+str(msg_time.clock_type))
        lag=now-msg_time
        lag_seconds=np.floor(lag.nanoseconds/1e9)
        lag_nanoseconds=lag.nanoseconds%1e9
        self.get_logger().info(f"Logging lag: {lag_seconds} seconds {lag_nanoseconds} nanoseconds")
        self.lag_list.append(lag)
    def dump_lags_callback(self,req,res):
        self.get_logger().info("Saving lags to file")
        pathlib.Path(req.path).write_text('\n'.join(map(str,self.lag_list)) + '\n')
        res.done=True
        self.lag_list=[]
        return res
def main():
    rclpy.init()
    laglogger=LagLogger(input_topic=args.input_topic)
    rclpy.spin(laglogger)
if __name__ == '__main__':
    main()
