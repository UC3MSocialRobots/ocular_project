#!/usr/bin/env python

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
Matches the predicted object ids to its corresponding names.

:author: Victor Gonzalez Pacheco
:maintainer: Victor Gonzalez Pacheco
"""

import roslib
roslib.load_manifest('ocular_interaction')

import sys
import rospy

from ocular_interaction import utils
from ocular_interaction import object_database_manager as odbm

from std_msgs.msg import String
from ocular.msg import SystemOutput


def _log_match(prefix, id_, name):
    """Log a match ID-Name."""
    logmsg = prefix + "(ID: {}, Name: {})".format(utils.green(str(id_)),
                                                  utils.green(name))
    rospy.loginfo(logmsg)


def _log_matched_names(msg, *names):
    """Log names and ids of predictions."""
    name, rgb_name, pcloud_name = names
    # rospy.loginfo("------------------------------------------")
    _log_match("Predicted Object      ", msg.id_2d_plus_3d, name)
    _log_match("RGB Prediction was    ", msg.id_2d, rgb_name)
    _log_match("PCloud Prediction was ", msg.id_3d, pcloud_name)
    rospy.loginfo("------------------------------------------")


class ObjectNameMatcher(object):

    """Node that matches the predicted object ids to its corresponding names."""

    def __init__(self, db_filename):
        """
        Constructor.

        Args:
            db_filename (str): Filename of the Object DB to load.
        """
        super(ObjectNameMatcher, self).__init__()
        self.db_filename = db_filename
        self.db = odbm.ObjectDBHelper(self.db_filename)
        rospy.on_shutdown(self.shutdown)
        rospy.Subscriber('ocular/final_object_id', SystemOutput, self.callback)
        self.pub = rospy.Publisher('recognized_object_name', String)

    def callback(self, msg):
        """Publish the name of the received object_id."""
        matched_name = self.seek_object_name(msg.id_2d_plus_3d)
        rgb_name = self.seek_object_name(msg.id_2d)
        pcloud_name = self.seek_object_name(msg.id_3d)
        _log_matched_names(msg, matched_name, rgb_name, pcloud_name)
        self.pub.publish(matched_name)

    def seek_object_name(self, object_id):
        """Seek object_id in object DB and returns its name."""
        return odbm.get_object_name_from_id(object_id, self.db)

    def shutdown(self):
        """Hook to be executed when rospy.shutdown is called."""
        pass

    def run(self):
        """Run the node."""
        rospy.spin()


_DEFAULT_NAME = 'object_name_matcher'

if __name__ == '__main__':
    db_filename = rospy.myargv(argv=sys.argv)[1]
    rospy.loginfo("Loaded Object Database file from: {}"
                  .format(utils.blue(db_filename)))
    try:
        rospy.init_node(_DEFAULT_NAME)
        rospy.loginfo("Initializing {} Node".format(rospy.get_name()))
        matcher = ObjectNameMatcher(db_filename)
        matcher.run()
    except rospy.ROSInterruptException:
        pass
