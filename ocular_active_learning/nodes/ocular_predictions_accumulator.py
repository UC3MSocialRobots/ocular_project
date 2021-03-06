#!/usr/bin/env python
# -*- coding: utf-8 -*-

# :license       LASR_UC3M v1.0, ver LICENCIA.txt

# Este programa es software libre: puede redistribuirlo y/o modificarlo
# bajo los terminos de la Licencia Academica Social Robotics Lab - UC3M
# publicada por la Universidad Carlos III de Madrid, tanto en su version 1.0
# como en una version posterior.

# Este programa se distribuye con la intencion de que sea util,
# pero SIN NINGUNA GARANTIA. Para mas detalles, consulte la
# Licencia Academica Social Robotics Lab - UC3M version 1.0 o posterior.

# Usted ha recibido una copia de la Licencia Academica Social
# Robotics Lab - UC3M en el fichero LICENCIA.txt, que tambien se encuentra
# disponible en <URL a la LASR_UC3Mv1.0>.
"""
Publishes accumulated predictions from the OCULAR learner_recognizer node.

:author: Victor Gonzalez-Pacheco
"""
import roslib
roslib.load_manifest('ocular_active_learning')
import rospy
from rospy import (Publisher, Subscriber)
from rospy import loginfo, logfatal

from ocular_active_learning import al_utils as alu

from ocular.msg import RecognizedObject
from ocular_msgs.msg import AccumulatedPredictions as Predictions
from rospy_utils.param_utils import load_params
from rospy_utils.func_utils import error_handler as eh


class AccumulatorNode(object):

    """
    AccumulatorNode: Accumulates predictions and publishes in a single msg.

    It accumulates predictions and publishes them every second.
    """

    def __init__(self):
        """Constructor."""
        rospy.init_node('ocular_predictions_accumulator', anonymous=True)
        loginfo("Initializing " + rospy.get_name() + " node...")
        rospy.on_shutdown(self.shutdown)

        with eh(logger=logfatal, log_msg="Couldn't load params", reraise=True):
            self.hz = load_params(['rate']).next()

        # Accumulates Hz items in per second. Ex: 30Hz -> ~30items/sec
        self.accumulator = alu.Accumulator(self.hz)

        # Publishers and Subscribers
        self.pub = Publisher('predictions', Predictions)
        Subscriber("object_id", RecognizedObject, self.callback)

    def callback(self, data):
        """Callback that publishes updated predictions when new msg is recv."""
        self.accumulator.append(data.object_id)
        if self.accumulator.isfull():
            rospy.logdebug("Accumulator full. Printing all predictions:")
            rospy.logdebug("{}".format(self.accumulator))
            predictions_rgb, predictions_pcloud = zip(*self.accumulator)
            msg = Predictions(rgb=predictions_rgb, pcloud=predictions_pcloud)
            try:
                self.pub.publish(msg)
            except ValueError as ve:
                rospy.logwarn(str(ve))

    def run(self):
        """Run (wrapper of ``rospy.spin()``."""
        rospy.spin()

    def shutdown(self):
        """Shudown hook to close the node."""
        loginfo('Shutting down ' + rospy.get_name() + ' node.')


if __name__ == '__main__':
    try:
        node = AccumulatorNode()
        node.run()
    except rospy.ROSInterruptException:
        pass
