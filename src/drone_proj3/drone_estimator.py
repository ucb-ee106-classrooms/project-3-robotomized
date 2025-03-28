import matplotlib.pyplot as plt
import numpy as np
import time

plt.rcParams["font.family"] = ["Arial"]
plt.rcParams["font.size"] = 14


class Estimator:
    """A base class to represent an estimator.

    This module contains the basic elements of an estimator, on which the
    subsequent DeadReckoning, Kalman Filter, and Extended Kalman Filter classes
    will be based on. A plotting function is provided to visualize the
    estimation results in real time.

    Attributes:
    ----------
        u : list
            A list of system inputs, where, for the ith data point u[i],
            u[i][0] is the thrust of the quadrotor
            u[i][1] is right wheel rotational speed (rad/s).
        x : list
            A list of system states, where, for the ith data point x[i],
            x[i][0] is translational position in x (m),
            x[i][1] is translational position in z (m),
            x[i][2] is the bearing (rad) of the quadrotor
            x[i][3] is translational velocity in x (m/s),
            x[i][4] is translational velocity in z (m/s),
            x[i][5] is angular velocity (rad/s),
        y : list
            A list of system outputs, where, for the ith data point y[i],
            y[i][1] is distance to the landmark (m)
            y[i][2] is relative bearing (rad) w.r.t. the landmark
        x_hat : list
            A list of estimated system states. It should follow the same format
            as x.
        dt : float
            Update frequency of the estimator.
        fig : Figure
            matplotlib Figure for real-time plotting.
        axd : dict
            A dictionary of matplotlib Axis for real-time plotting.
        ln* : Line
            matplotlib Line object for ground truth states.
        ln_*_hat : Line
            matplotlib Line object for estimated states.
        canvas_title : str
            Title of the real-time plot, which is chosen to be estimator type.

    Notes
    ----------
        The landmark is positioned at (0, 5, 5).
    """

    # noinspection PyTypeChecker
    def __init__(self, is_noisy=False):
        self.u = []
        self.x = []
        self.y = []
        self.x_hat = []  # Your estimates go here!
        self.update_times = []
        self.t = []
        self.fig, self.axd = plt.subplot_mosaic(
            [["xz", "phi"], ["xz", "x"], ["xz", "z"]], figsize=(20.0, 10.0)
        )
        (self.ln_xz,) = self.axd["xz"].plot([], "o-g", linewidth=2, label="True")
        (self.ln_xz_hat,) = self.axd["xz"].plot([], "o-c", label="Estimated")
        (self.ln_phi,) = self.axd["phi"].plot([], "o-g", linewidth=2, label="True")
        (self.ln_phi_hat,) = self.axd["phi"].plot([], "o-c", label="Estimated")
        (self.ln_x,) = self.axd["x"].plot([], "o-g", linewidth=2, label="True")
        (self.ln_x_hat,) = self.axd["x"].plot([], "o-c", label="Estimated")
        (self.ln_z,) = self.axd["z"].plot([], "o-g", linewidth=2, label="True")
        (self.ln_z_hat,) = self.axd["z"].plot([], "o-c", label="Estimated")
        self.canvas_title = "N/A"

        # Defined in dynamics.py for the dynamics model
        # m is the mass and J is the moment of inertia of the quadrotor
        self.gr = 9.81
        self.m = 0.92
        self.J = 0.0023
        # These are the X, Y, Z coordinates of the landmark
        self.landmark = (0, 5, 5)

        # This is a (N,12) where it's time, x, u, then y_obs
        if is_noisy:
            with open("noisy_data.npy", "rb") as f:
                self.data = np.load(f)
        else:
            with open("data.npy", "rb") as f:
                self.data = np.load(f)

        self.dt = self.data[-1][0] / self.data.shape[0]

    def run(self):
        for i, data in enumerate(self.data):
            self.t.append(np.array(data[0]))
            self.x.append(np.array(data[1:7]))
            self.u.append(np.array(data[7:9]))
            self.y.append(np.array(data[9:12]))
            if i == 0:
                self.x_hat.append(self.x[-1])
            else:
                self.update(i)
        return self.x_hat

    def update(self, _):
        raise NotImplementedError

    def plot_init(self):
        self.axd["xz"].set_title(self.canvas_title)
        self.axd["xz"].set_xlabel("x (m)")
        self.axd["xz"].set_ylabel("z (m)")
        self.axd["xz"].set_aspect("equal", adjustable="box")
        self.axd["xz"].legend()
        self.axd["phi"].set_ylabel("phi (rad)")
        self.axd["phi"].set_xlabel("t (s)")
        self.axd["phi"].legend()
        self.axd["x"].set_ylabel("x (m)")
        self.axd["x"].set_xlabel("t (s)")
        self.axd["x"].legend()
        self.axd["z"].set_ylabel("z (m)")
        self.axd["z"].set_xlabel("t (s)")
        self.axd["z"].legend()
        plt.tight_layout()

    def plot_update(self, _):
        self.plot_xzline(self.ln_xz, self.x)
        self.plot_xzline(self.ln_xz_hat, self.x_hat)
        self.plot_philine(self.ln_phi, self.x)
        self.plot_philine(self.ln_phi_hat, self.x_hat)
        self.plot_xline(self.ln_x, self.x)
        self.plot_xline(self.ln_x_hat, self.x_hat)
        self.plot_zline(self.ln_z, self.x)
        self.plot_zline(self.ln_z_hat, self.x_hat)

    def plot_xzline(self, ln, data):
        if len(data):
            x = [d[0] for d in data]
            z = [d[1] for d in data]
            ln.set_data(x, z)
            self.resize_lim(self.axd["xz"], x, z)

    def plot_philine(self, ln, data):
        if len(data):
            t = self.t
            phi = [d[2] for d in data]
            ln.set_data(t, phi)
            self.resize_lim(self.axd["phi"], t, phi)

    def plot_xline(self, ln, data):
        if len(data):
            t = self.t
            x = [d[0] for d in data]
            ln.set_data(t, x)
            self.resize_lim(self.axd["x"], t, x)

    def plot_zline(self, ln, data):
        if len(data):
            t = self.t
            z = [d[1] for d in data]
            ln.set_data(t, z)
            self.resize_lim(self.axd["z"], t, z)

    # noinspection PyMethodMayBeStatic
    def resize_lim(self, ax, x, y):
        xlim = ax.get_xlim()
        ax.set_xlim([min(min(x) * 1.05, xlim[0]), max(max(x) * 1.05, xlim[1])])
        ylim = ax.get_ylim()
        ax.set_ylim([min(min(y) * 1.05, ylim[0]), max(max(y) * 1.05, ylim[1])])

    def calc_avg_update_time(self):
        """Calculate the average update time."""
        return np.mean(np.array(self.update_times))

    def calc_error(self):
        """Calculate the RMSE between the estimated and true states."""
        actual_states = np.array(self.x)
        estimated_states = np.array(self.x_hat)
        estimated_states = np.vstack(
            [
                estimated_states[:, 0],
                estimated_states[:, 1],
                np.arctan2(
                    np.sin(estimated_states[:, 2]), np.cos(estimated_states[:, 2])
                ),
                estimated_states[:, 3],
                estimated_states[:, 4],
                estimated_states[:, 5],
            ]
        )
        actual_states = np.vstack(
            [
                actual_states[:, 0],
                actual_states[:, 1],
                np.arctan2(np.sin(actual_states[:, 2]), np.cos(actual_states[:, 2])),
                actual_states[:, 3],
                actual_states[:, 4],
                actual_states[:, 5],
            ]
        )

        return np.linalg.norm(estimated_states - actual_states, axis=1)


class OracleObserver(Estimator):
    """Oracle observer which has access to the true state.

    This class is intended as a bare minimum example for you to understand how
    to work with the code.

    Example
    ----------
    To run the oracle observer:
        $ python drone_estimator_node.py --estimator oracle_observer
    """

    def __init__(self, is_noisy=False):
        super().__init__(is_noisy)
        self.canvas_title = "Oracle Observer"

    def update(self, _):
        self.x_hat.append(self.x[-1])


class DeadReckoning(Estimator):
    """Dead reckoning estimator.

    Your task is to implement the update method of this class using only the
    u attribute and x0. You will need to build a model of the unicycle model
    with the parameters provided to you in the lab doc. After building the
    model, use the provided inputs to estimate system state over time.

    The method should closely predict the state evolution if the system is
    free of noise. You may use this knowledge to verify your implementation.

    Example
    ----------
    To run dead reckoning:
        $ python drone_estimator_node.py --estimator dead_reckoning
    """

    def __init__(self, is_noisy=False):
        super().__init__(is_noisy)
        self.canvas_title = "Dead Reckoning"

        def f(x, u):
            first_term = np.array([x[3], x[4], x[5], 0, -self.gr, 0]).reshape(6, 1)
            second_term = np.array(
                [
                    [0, 0],
                    [0, 0],
                    [0, 0],
                    [-np.sin(x[2]) / self.m, 0],
                    [np.cos(x[2]) / self.m, 0],
                    [0, 1 / self.J],
                ]
            )
            u_term = np.array([u[0], u[1]]).reshape(2, 1)
            return first_term + second_term @ u_term

        self.model = lambda x, u: np.array(x).reshape((6, 1)) + f(x, u) * self.dt

    def update(self, _):
        if len(self.x_hat) > 0:
            start_time = time.perf_counter()
            # x_dot = f = [x_dot, z_dot, phi_dot, x_ddot, z_ddot, phi_ddot]
            self.x_hat.append(tuple(self.model(self.x_hat[-1], self.u[-1]).flatten()))
            self.update_times.append(time.perf_counter() - start_time)


# noinspection PyPep8Naming
class ExtendedKalmanFilter(Estimator):
    """Extended Kalman filter estimator.

    Your task is to implement the update method of this class using the u
    attribute, y attribute, and x0. You will need to build a model of the
    unicycle model and linearize it at every operating point. After building the
    model, use the provided inputs and outputs to estimate system state over
    time via the recursive extended Kalman filter update rule.

    Hint: You may want to reuse your code from DeadReckoning class and
    KalmanFilter class.

    Attributes:
    ----------
        landmark : tuple
            A tuple of the coordinates of the landmark.
            landmark[0] is the x coordinate.
            landmark[1] is the y coordinate.
            landmark[2] is the z coordinate.

    Example
    ----------
    To run the extended Kalman filter:
        $ python drone_estimator_node.py --estimator extended_kalman_filter
    """

    def __init__(self, is_noisy=False):
        super().__init__(is_noisy)
        self.canvas_title = "Extended Kalman Filter"
        # You may define the Q, R, and P matrices below.
        self.Q = np.diag([2, 0.03, 7, 2, 13, 0.5])  # covariance matrix fo process noise
        self.R = np.diag([1.7, 0.5])  # covariance matrix of measurement noise
        self.P = np.diag(
            [2, 90, 0.2, 2, 50, 0.5]
        )  # covariance matrix of estimation error

    # noinspection DuplicatedCode
    def update(self, i):
        if len(self.x_hat) > 0:  # and self.x_hat[-1][0] < self.x[-1][0]:
            start_time = time.perf_counter()
            # You may use self.u, self.y, and self.x[0] for estimation
            # state extrapolation
            x_hat_prev = np.array(self.x_hat[-1])
            # print("x_hat_prev: ", x_hat_prev[:3])
            u_prev = np.array(self.u[-1])
            x_pred = self.g(x_hat_prev, u_prev)  # calculate g(x_hat, u)
            # print("x_pred: ", x_pred.flatten()[:3])

            # dynamics linearization ~ calculate A[t+1]
            self.A = self.approx_A(x_hat_prev, u_prev)  # Jacobian of g(x, u) w.r.t. x

            # covariance extrapolation
            P_pred = self.A @ self.P @ self.A.T + self.Q

            # measurement linearization
            # calculate C[t+1] ~ Jacobian of h(x) w.r.t. x
            self.C = self.approx_C(x_pred)

            # Kalman gain
            K = P_pred @ self.C.T @ np.linalg.inv(self.C @ P_pred @ self.C.T + self.R)

            # state update
            self.x_hat.append(
                tuple(
                    (
                        x_pred
                        + K
                        @ (
                            np.array(self.y[-1]).reshape((2, 1))
                            - self.h(x_pred, self.landmark)
                        )
                    )
                    .flatten()
                    .tolist()
                )  # unpack the tuple returned by the model
            )

            # covariance update
            self.P = (np.eye(self.P.shape[0]) - K @ self.C) @ P_pred
            self.update_times.append(time.perf_counter() - start_time)

    def g(self, x, u):
        """Model dynamics of quadrotor"""
        first_term = np.array([x[3], x[4], x[5], 0, -self.gr, 0]).reshape(6, 1)
        second_term = np.array(
            [
                [0, 0],
                [0, 0],
                [0, 0],
                [-np.sin(x[2]) / self.m, 0],
                [np.cos(x[2]) / self.m, 0],
                [0, 1 / self.J],
            ]
        )
        u_term = np.array([u[0], u[1]]).reshape(2, 1)
        f_term = first_term + second_term @ u_term
        return np.array(x).reshape((6, 1)) + f_term * self.dt

    def h(self, x, y_obs):
        """Measurement model of the quadrotor"""
        return np.array(
            [
                np.sqrt(
                    (x[0] - y_obs[0]) ** 2
                    + (x[1] - y_obs[1]) ** 2
                    + (x[2] - y_obs[2]) ** 2
                ),
                x[2],
            ]
        )

    def approx_A(self, x, u):
        """Approximate the dynamics Jacobian matrix"""
        A_bar = np.eye(6)
        A_bar[3:, :3] += np.eye(3) * self.dt
        A_bar[3, 2] += -np.cos(x[2]) * u[0] / self.m * self.dt
        A_bar[4, 2] += -np.sin(x[2]) * u[0] / self.m * self.dt
        return A_bar

    def approx_C(self, x):
        """Approximate the measurement Jacobian matrix"""
        C_bar = np.zeros((2, 6))
        C_bar[0, 0] = (x[0] - self.landmark[0]) / np.sqrt(
            (x[0] - self.landmark[0]) ** 2
            + self.landmark[1] ** 2
            + (x[1] - self.landmark[2]) ** 2
        )
        C_bar[0, 1] = (x[1] - self.landmark[2]) / np.sqrt(
            (x[0] - self.landmark[0]) ** 2
            + self.landmark[1] ** 2
            + (x[1] - self.landmark[2]) ** 2
        )
        C_bar[1, 2] = 1
        return C_bar
