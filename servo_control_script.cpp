#include "ros/ros.h"
#include "dynamixel_position_control/MsgDynamixel.h"
#include "dynamixel_msgs/JointState.h"

#define GOAL_POS 0
#define CURRENT_POS 1
#define ERROR 2
#define LOAD 3
#define ERROR_POS 0.01
#define ERROR_NEG -0.01

void motor_command(ros::Publisher dynamixel_publisher); // Command motor to move
bool motor_init(); // Initialize motor variables

struct Motor {
    float motor_state[4]; // Motor states (goal position, current position, etc.)
    int state;            // FSM state
    bool moving;          // Indicates if the motor is still moving
    dynamixel_position_control::MsgDynamixel msg;
} MX28;

// Initialize motor variables
bool motor_init() {
    MX28.state = 0; // Initial state
    for (int i = 0; i < 4; i++) MX28.motor_state[i] = 0xff; // Reset motor states
    MX28.moving = false;
    MX28.msg.data = 0; // Start position at zero
    return true;
}

// Callback for receiving current motor state
void msgCallback(const dynamixel_msgs::JointState::ConstPtr& msg) {
    MX28.motor_state[GOAL_POS] = msg->goal_pos;
    MX28.motor_state[CURRENT_POS] = msg->current_pos;
    MX28.motor_state[ERROR] = msg->error;
    MX28.motor_state[LOAD] = msg->load;
    MX28.moving = msg->is_moving;
}

int main(int argc, char** argv) {
    ros::init(argc, argv, "dynamixel_zero_position");
    ros::NodeHandle nh;

    if (!motor_init()) {
        ROS_ERROR("Failed to initialize motor.");
        return 0;
    }

    // Publisher for sending position commands
    ros::Publisher dynamixel_publisher = nh.advertise<dynamixel_position_control::MsgDynamixel>("tilt_controller/command", 100);

    // Subscriber for receiving motor state
    ros::Subscriber dynamixel_subscriber = nh.subscribe("tilt_controller/state", 100, msgCallback);

    ros::Rate loop_rate(10); // Set loop rate (10 Hz)

    while (ros::ok()) {
        // Wait for callbacks
        ros::spinOnce();

        // Command motor to move toward position 0
        motor_command(dynamixel_publisher);

        // Stop the loop if the motor is at position 0
        if (!MX28.moving && 
            (MX28.motor_state[CURRENT_POS] >= -ERROR_POS) && 
            (MX28.motor_state[CURRENT_POS] <= ERROR_POS)) {
            ROS_INFO("Motor reached position 0. Stopping...");
            break;
        }

        loop_rate.sleep();
    }

    return 0;
}

// Command motor to move toward position 0
void motor_command(ros::Publisher dynamixel_publisher) {
    if (MX28.state == 0) { // TX state
        MX28.msg.data = 0.0; // Command position 0
        dynamixel_publisher.publish(MX28.msg);
        ROS_INFO("Commanded motor to position 0.");
        MX28.state = 1; // Transition to RX state
    } else if (MX28.state == 1) { // RX state
        if ((MX28.motor_state[CURRENT_POS] >= -ERROR_POS) && 
            (MX28.motor_state[CURRENT_POS] <= ERROR_POS)) {
            ROS_INFO("Motor is at position 0.");
        } else {
            MX28.state = 0; // Return to TX state to re-send the command
        }
    }
}
