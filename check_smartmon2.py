#!/usr/bin/python

# -*- coding: iso8859-1 -*-
#
# $Id: version.py 133 2006-03-24 10:30:20Z fuller $
#
# check_smartmon
# Copyright (C) 2006  daemogorgon.net
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

#
# MOD by basos (basos<dot<g<at<gmx<dot<net)
# - add no check standby option
# - add all atributes checking logic
# - add infastructure for arbitrary raw attribute checking
#
# v1.1

"""Package versioning
"""


import os.path
import sys
import re

from optparse import OptionParser


__author__ = "fuller <fuller@daemogorgon.net>"
__version__ = "$Revision$"


# application wide verbosity (can be adjusted with -v [0-3])
_verbosity = 0


def parseCmdLine(args):
        """Commandline parsing."""

        usage = "usage: %prog [options]"
        version = "%%prog %s" % (__version__)

        parser = OptionParser(usage=usage, version=version)
        parser.add_option("-d", "--device", action="store", dest="device", default="", metavar="DEVICE",
                        help="device to check")
        parser.add_option("-v", "--verbosity", action="store",
                        dest="verbosity", type="int", default=0,
                        metavar="LEVEL", help="set verbosity level to LEVEL; defaults to 0 (quiet), \
                                        possible values go up to 3")
        parser.add_option("-w", "--warning-threshold", metavar="TEMP", action="store",
                        type="int", dest="warningThreshold", default="50",
                        help="set temperature warning threshold to given temperature (defaults to 50)")
        parser.add_option("-c", "--critical-threshold", metavar="TEMP", action="store",
                        type="int", dest="criticalThreshold", default="55",
                        help="set temperature critical threshold to given temperature (defaults to 55)")
        parser.add_option("-T", "--temperature-attrid", metavar="ID", action="store",
                        type="int", dest="tempAttrId", default="190",
                        help="set the temperature smart attribute id (defaults to 190)")
        parser.add_option("-r", "--raw-attribute", metavar="ID WARN CRIT", action="append",
                        type="int", dest="rawAttrs", nargs=3,
                        help="define raw attributes to monitor (excluding temperature). Each attribute is defined by three space separated numbers: id, warn, crit. This option is accepted multiple times, one for each attribute.")
        parser.add_option("-n", "--no-check-standby", metavar="BOOL", action="store_true",
                        dest="noCheckStandby", default=False,
                        help="do not check when disk status is standby (most disks do not spin in this state) (defaults to false)")
        parser.add_option("-s", "--smartctl-command", metavar="CMD", action="store",
                        type="string", dest="smartctlPath", default="/usr/sbin/smartctl",
                        help="set the smartctl full system path or sudo prefixed command (defaults to /usr/sbin/smartctl)")
        parser.add_option("-x", "--smartctl-xtra-args", metavar="ARGS", action="store",
                        type="string", dest="smartctlArgs", default="",
                        help="set extra smartctl args (excluding AHn).")
        return parser.parse_args(args)
# end


def checkDevice(path):
        """Check if device exists and permissions are ok.

        Returns:
                - 0 ok
                - 1 no such device
                - 2 no read permission given
        """

        vprint(3, "Check if %s does exist and can be read" % path)
        if not os.access(path, os.F_OK):
                return (1, "UNKNOWN: no such device found")
        # Allow sudo execution
        #elif not os.access(path, os.R_OK):
        #        return (2, "UNKNOWN: no read permission given")
        else:
                return (0, "")
        # fi
# end


#def checkSmartMonTools(path):
#        """Check if smartctl is available and can be executed.
#
#        Returns:
#                - 0 ok
#                - 1 no such file
#                - 2 cannot execute file
#        """
#
#        vprint(3, "Check if %s does exist and can be read" % path)
#        if not os.access(path, os.F_OK):
#                return (1, "UNKNOWN: cannot find %s" % path)
#        elif not os.access(path, os.X_OK):
#                return (2, "UNKNOWN: cannot execute %s" % path)
#        else:
#                return (0, "")
#        # fi
## end


def callSmartMonTools(path, device, noCheckStandbyFlag, xtraArgs):
        # get health status
        noCheckStandby = "-n standby " if noCheckStandbyFlag else ""
        xtraArgs = xtraArgs+" " if xtraArgs else ""
        cmd = "%s -AH %s%s%s" % (path, noCheckStandby, xtraArgs, device)
        vprint(3, "Get device health/attribute status: %s" % cmd)
        (child_stdin, child_stdout, child_stderr) = os.popen3(cmd)
        line = child_stderr.readline()
        if len(line):
                return (3, "UNKNOWN: call exits unexpectedly (%s)" % line, "")
        smartStatusOutput = ""
        for line in child_stdout:
                smartStatusOutput = smartStatusOutput + line
        # done

        return (0 ,"", smartStatusOutput)
# end


def createReturnInfo(healthMessage, attrSpecs):
        """Parse smartctl output

        attrSpecs dict of attrSpec tuples {attrid: (warn, crit)}
        Create nagios return information according to given thresholds.
        """

        def checkAttr(id, raw, attrSpecs):
          id = int(id)
          if id not in attrSpecs:
              return (-1,None,None)
          attrSpec = attrSpecs[id]
          raw = int(raw)
          if raw >= attrSpec[1]:
              return (2,)+attrSpec ; # crit (val >= crit)
          elif raw >= attrSpec[0]:
              return (1,)+attrSpec; # warn (val >= warn)
          return (0,)+attrSpec; # ok
        #def

        def formatAttr(s_id, s_name, s_failed, s_value, s_thres):
            return "Attribute "+str(s_name)+" ("+str(s_id)+") seems to fail ("+(str(s_failed) if s_failed != '-' else \
              str(s_value)+"<="+str(s_thres))+")"

        def pipeStuff(s_name, s_value, s_thres, s_cthres = None, s_min = "0", s_max = "254"):
            if (None == s_cthres): s_cthres = s_thres
            return "|"+str(s_name)+"="+str(s_value)+";"+str(s_thres)+";"+str(s_cthres)+((";"+s_min+((";"+s_max) if s_max != None else "")) if s_min != None else "")

        # parse health status
        #
        statusLine = ""
        lines = healthMessage.split("\n")
        getNext = 0
        healthStatus = ''
        temperStuff = (None, "Temperature_not_found", 0 , 0)
        in_attrs = 0
        ret = (3, "UNKNNOWN: smartctl encountered an error")
        for line in lines:
            if healthStatus == '' and re.search(r"^SMART overall-health self-assessment test result", line):
                ps = line.split()
                healthStatus = ps[-1]
                vprint(3, "Health status: %s" % healthStatus)
                # this is absolutely critical!
                if healthStatus != "PASSED":
                     ret = (2, "CRITICAL: SMART overall health test failed")
                else:
                    ret = (0, "OK: device is functional and stable")
                continue;
                # fi
            if in_attrs == 1 and (not line or not re.search(r"\d+", line.split()[0])):
                vprint(3, "End of Attributes parsing");
                in_attrs = 0
            if in_attrs:
                ps = line.split()
                s_id, s_name, s_flag, s_value, s_worst, s_thres, s_type, s_updated, s_failed, s_raw = \
                    ps[0], ps[1], ps[2], ps[3], ps[4], ps[5], ps[6], ps[7], ps[8], ps[9]
                vprint(2, "Checking Attr: %s (%s), v: %s (%s)" % (s_name, s_id, s_value, s_raw))
                if (s_failed != '-' or int(s_value) <= int(s_thres)):
                    if s_type.lower() == 'pre-fail' :
                        if s_failed.lower() != 'in_the_past':
                            ret = (2, "CRITICAL: "+formatAttr(s_id, s_name, s_failed, s_value, s_thres) + \
                                pipeStuff(s_name, s_value, s_thres))
                        elif ret[0] < 2:
                            ret = (1, "WARNING: "+formatAttr(s_id, s_name, s_failed, s_value, s_thres) + \
                                pipeStuff(s_name, s_value, s_thres))
                    elif ret[0] < 2 and s_failed.lower() != 'in_the_past':
                        ret = (1, "WARNING: "+formatAttr(s_id, s_name, s_failed, s_value, s_thres) + \
                            pipeStuff(s_name, s_value, s_thres))
                # fi
                tmp = checkAttr(s_id, s_raw, attrSpecs)
                if tmp[0] > 0:
                    if ret[0] < 2:
                        #ret = (tmp[0], "CRITICAL" if tmp[0] == 2 else "WARNING"+": Attribute raw "+str(s_name)+" ("+str(s_id)+") over "+("critical" if tmp[0] == 2 \
                          #else "warning")+"threshold ("+str(s_raw)+">="+str(tmp[2 if tmp[0] == 2 else 1]+")"))
                        vprint(2, "Attr "+str(s_id)+", "+str(s_raw)+" over thres "+str(tmp));
                        ret = (tmp[0], ("CRITICAL" if tmp[0] == 2 else "WARNING")+": " + \
                            formatAttr(s_id, s_name, "Raw_limits", s_raw, tmp[2 if tmp[0] == 2 else 1]) + \
                            pipeStuff(s_name, s_raw, tmp[1], tmp[2], *(("0", "100") if len(tmp) == 4 and tmp[3] else ())))
                elif tmp[0] == 0 and len(tmp) == 4 and tmp[3]:
                    # found temperature
                    temperStuff = (s_name, s_raw) + tmp[1:3]
            elif re.search(r"ID.?\s+ATTRIBUTE_NAME\s+FLAG\s+VALUE\s+WORST\s+THRESH\s+TYPE\s+UPDATED\s+WHEN_FAILED\s+RAW_VALUE", line):
                vprint(3, "Start of Attributes parsing")
                in_attrs = 1
            else:
               vprint(3, "Ommiting smartctl row: %s" % line)
          # ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
        # done
        if ret[0] == 0 and temperStuff[0] != None:
            temperStuff = temperStuff + ("0", "100")
            ret = (0, ret[1] + pipeStuff(*temperStuff))

        if ret[0] == 3:
            vprint(3, "smartctl error, output: %s" % healthMessage);
        return ret
        ##(0, "OK: device is functional and stable (temperature: %d)" % temperature)
# end


def exitWithMessage(value, message):
        """Exit with given value and status message."""

        print message
        sys.exit(value)
# end


def vprint(level, message):
        """Verbosity print.

        Decide according to the given verbosity level if the message will be
        printed to stdout.
        """

        if level <= verbosity:
                print message
        # fi
# end


if __name__ == "__main__":
        (options, args) = parseCmdLine(sys.argv)
        verbosity = options.verbosity

        vprint(2, "Get device name")
        device = options.device
        vprint(1, "Device: %s" % device)

        # check if we can access 'path'
        vprint(2, "Check device")
        (value, message) = checkDevice(device)
        if value != 0:
                exitWithMessage(3, message)
        # fi

        # check if we have smartctl available
        #(value, message) = checkSmartMonTools(options.smartctlPath)
        #if value != 0:
        #        exitWithMessage(3, message)
        # fi
        vprint(1, "Path to smartctl: %s" % options.smartctlPath)

        # call smartctl and parse output
        vprint(2, "Call smartctl")
        (value, message, healthStatusOutput) = callSmartMonTools(options.smartctlPath, device, options.noCheckStandby, options.smartctlArgs)
        if value != 0:
                exitWithMessage(value, message)

        vprint(2, "Parse smartctl output and return info")
        attrs = {}
        if options.rawAttrs:
            for at in options.rawAttrs:
                attrs[at[0]] = at[1:3]
        attrs[options.tempAttrId] = (options.warningThreshold, options.criticalThreshold, True)
        (value, message) = createReturnInfo(healthStatusOutput, attrs)

        # exit program
        exitWithMessage(value, message)

# fi
