# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import os

from cliff import command
from cliff import lister
from cliff import show

from os_sandbox import conf
from os_sandbox import helpers
from os_sandbox import sandbox
from os_sandbox import template


class SandboxList(lister.Lister):
    """Show a list of sandboxes created on the sandbox host."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(SandboxList, self).get_parser(prog_name)
        conf.add_common_args(parser)
        return parser

    def take_action(self, parsed_args):
        sandboxes = []
        helpers.ensure_state_dir(parsed_args)
        sandboxes = sandbox.Sandboxes(parsed_args)
        return (
            ('Sandbox', 'Status', 'Template'),
            (
                (
                    sb.full_name,
                    sb.status,
                    sb.template.name
                )
                for sb in sandboxes
            )
        )


class SandboxShow(command.Command):
    """Show detailed information about a single sandbox."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(SandboxShow, self).get_parser(prog_name)
        conf.add_common_args(parser)
        parser.add_argument('name', help='Name of the sandbox to show')
        return parser

    def take_action(self, parsed_args):
        sandboxes = []
        state_dir = helpers.ensure_state_dir(parsed_args)
        sb_name = parsed_args.name
        sb = sandbox.Sandbox(parsed_args, sb_name)
        if not sb.exists():
            msg = "A sandbox with name {0} does not exist.".format(sb_name)
            raise RuntimeError(msg)
            
        self.app.stdout.write('Name: ' + sb.full_name + '\n')
        self.app.stdout.write('Status: ' + sb.status + '\n')
        self.app.stdout.write('Template: ' + sb.template.name + '\n')
        self.app.stdout.write('Networks:\n')
        line = "  {:<18} {:<14} {:<10}\n"
        for net in sb.networks:
            net_line = line.format(net.name, net.status, net.cidr)
            self.app.stdout.write(net_line)
        self.app.stdout.write('Nodes:\n')
        for node in sb.nodes:
            services_str = ",".join(node.services)
            node_line = line.format(node.name, node.status, services_str)
            self.app.stdout.write(node_line)


class SandboxCreate(command.Command):
    """Creates a sandbox with a given name."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(SandboxCreate, self).get_parser(prog_name)
        conf.add_common_args(parser)
        parser.add_argument('name', help='Name of the sandbox')
        parser.add_argument('-t', '--template',
                            required=True,
                            help='Name of the template to use for the sandbox')
        return parser

    def take_action(self, parsed_args):
        state_dir = helpers.ensure_state_dir(parsed_args)

        sb_name = parsed_args.name
        tpl_name = parsed_args.template
        sb = sandbox.Sandbox(parsed_args, sb_name)
        sb.create()
        
        if self.app.options.verbose_level > 0:
            self.app.console_ok(newline=False)
            msg = " Created sandbox {0} using template {1}\n"
            msg = msg.format(sb_name, tpl_name)
            self.app.stdout.write(msg)


class SandboxDelete(command.Command):
    """Deletes a sandbox with a given name."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(SandboxDelete, self).get_parser(prog_name)
        conf.add_common_args(parser)
        parser.add_argument('name', help='Name of the sandbox to delete')
        parser.add_argument('-f', '--force', action="store_true",
                            default=False,
                            help="Force the deletion of the sandbox, ignoring "
                                 "any errors that may have been encountered "
                                 "in trying to shut down the sandbox.")
        return parser

    def take_action(self, parsed_args):
        state_dir = helpers.ensure_state_dir(parsed_args)

        sb_name = parsed_args.name
        try:
            sb = sandbox.Sandbox(parsed_args, sb_name)
        except Exception:
            if parsed_args.force:
                sandbox.Sandbox.force_delete(sb_name)
            else:
                raise

        if not sb.exists():
            msg = "A sandbox with name {0} does not exist.".format(sb_name)
            raise RuntimeError(msg)

        sb.delete()

        if self.app.options.verbose_level > 0:
            self.app.console_ok(newline=False)
            msg = " Deleted sandbox {0}\n"
            msg = msg.format(sb_name)
            self.app.stdout.write(msg)


class SandboxStart(command.Command):
    """Starts a sandbox with a given name."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(SandboxStart, self).get_parser(prog_name)
        conf.add_common_args(parser)
        parser.add_argument('name', help='Name of the sandbox to start')
        return parser

    def take_action(self, parsed_args):
        state_dir = helpers.ensure_state_dir(parsed_args)

        sb_name = parsed_args.name
        sb = sandbox.Sandbox(parsed_args, sb_name)
        if not sb.exists():
            msg = "A sandbox with name {0} does not exist.".format(sb_name)
            raise RuntimeError(msg)

        sb.start()

        if self.app.options.verbose_level > 0:
            self.app.console_ok(newline=False)
            msg = " Started sandbox {0}\n"
            msg = msg.format(sb_name)
            self.app.stdout.write(msg)


class SandboxStop(command.Command):
    """Stops a sandbox with a given name."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(SandboxStop, self).get_parser(prog_name)
        conf.add_common_args(parser)
        parser.add_argument('name', help='Name of the sandbox to stop')
        return parser

    def take_action(self, parsed_args):
        state_dir = helpers.ensure_state_dir(parsed_args)

        sb_name = parsed_args.name
        sb = sandbox.Sandbox(parsed_args, sb_name)
        if not sb.exists():
            msg = "A sandbox with name {0} does not exist.".format(sb_name)
            raise RuntimeError(msg)

        sb.stop()

        if self.app.options.verbose_level > 0:
            self.app.console_ok(newline=False)
            msg = " Stopped sandbox {0}\n"
            msg = msg.format(sb_name)
            self.app.stdout.write(msg)
