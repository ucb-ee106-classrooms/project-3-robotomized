#!/usr/bin/env python3
import rospy
from Estimator import OracleObserver, DeadReckoning, KalmanFilter, ExtendedKalmanFilter
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

plt.show(block=True)


def spin(estimator):
    """Custom function to replace rospy.spin().

    Keep the ROS process alive while doing real-time plotting. The default
    rospy.spin() will break the real-time plotting function.

    Parameters
    ----------
    estimator : Estimator
        The instance of the estimator

    Returns
    -------
        None
    """
    # noinspection PyUnusedLocal
    anim = FuncAnimation(
        estimator.fig,
        estimator.plot_update,
        init_func=estimator.plot_init,
        cache_frame_data=False,
    )
    plt.show(block=True)  # This functions the same as rospy.spin()


def main():
    """Entry point of the estimator node.

    Returns
    -------
        None
    """
    rospy.init_node("estimator_node")
    estimator_type = rospy.get_param("estimator_type")
    if estimator_type == "oracle_observer":
        estimator = OracleObserver()
    elif estimator_type == "dead_reckoning":
        estimator = DeadReckoning()
    elif estimator_type == "kalman_filter":
        estimator = KalmanFilter()
    elif estimator_type == "extended_kalman_filter":
        estimator = ExtendedKalmanFilter()
    else:
        raise RuntimeError("Estimator type {} not supported".format(estimator_type))
    rospy.loginfo("Invoking estimator {}...".format(estimator_type))
    spin(estimator)
    print("Times: ", len(estimator.update_times))
    print("Trajectory Error: ", len(estimator.x_hat))
    print("Actual Trajectory: ", len(estimator.x))
    error_str = ""
    for e in estimator.calc_error():
        error_str += str(e) + ","
    pos_error = np.linalg.norm(estimator.calc_error()[2:4])
    print("Position Error: ", pos_error)
    error_str += str(pos_error)
    error_str += "," + str(estimator.calc_avg_update_time())
    print("Errors: ", error_str)


if __name__ == "__main__":
    main()
