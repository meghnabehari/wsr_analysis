#include "ros/ros.h"
#include "sensor_msgs/JointState.h"
#include "std_msgs/Float64.h"

float joint_angle = 0.0; // Current joint position (global for callback)
const float target_position = 0.0; // Target servo position

// Callback to read joint states
void CallJointState(const sensor_msgs::JointState::ConstPtr& msg) {
    joint_angle = msg->position[0]; // Assume index 0 corresponds to the servo joint
    ROS_INFO("Current Position: %f", joint_angle);
}

int main(int argc, char** argv) {
    ros::init(argc, argv, "set_servo_position");
    ros::NodeHandle nh;

    // Subscriber to joint states (adjust topic name if necessary)
    ros::Subscriber joint_state_sub = nh.subscribe("/wsr_antenna_motor/joint_states", 10, CallJointState);

    // Publisher to command the servo (adjust topic name if necessary)
    ros::Publisher servo_command_pub = nh.advertise<std_msgs::Float64>("/wsr_antenna_motor/command", 10);

    ros::Rate loop_rate(10); // 10 Hz loop rate

    while (ros::ok()) {
        ros::spinOnce(); // Process callbacks

        // Check if the servo is already at the target position
        if (fabs(joint_angle - target_position) <= 0.01) { // Error threshold
            ROS_INFO("Servo reached target position: %f", target_position);
            break;
        }

        // Publish the target position command
        std_msgs::Float64 command_msg;
        command_msg.data = target_position;
        servo_command_pub.publish(command_msg);
        ROS_INFO("Servo to position: %f", target_position);
		

        loop_rate.sleep();
		
    }

    ROS_INFO("Servo position set successfully.");
    return 0;
}
