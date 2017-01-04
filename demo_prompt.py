#! /usr/bin/env python2

from __future__ import unicode_literals

import api

from prompt_toolkit import prompt, AbortAction
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.contrib.completers import WordCompleter

import argparse

class BaseParser(argparse.ArgumentParser):
    def parse_args(*args, **kargs):
        try:
            return argparse.ArgumentParser.parse_args(*args, **kargs)
        except SystemExit:
            return None

class ALCmd():
    
    def __init__(self):
        self.account_id = None
        self.environment_id = None
        self.update_prompt()
    
    def run(self):
        completer = WordCompleter(["context", "set_deployment_mode", "exit", "help"])
        history = InMemoryHistory()
        while True:
            try:
                text = prompt(self.prompt,
                              completer=completer,
                              history=history,
                              on_abort=AbortAction.RETRY)
                command = text.split(" ", 1)[0]
                try:
                    params = text.split(" ", 1)[1]
                except IndexError:
                    params = ""
                if len(command) == 0:
                    continue
                if command == "set_deployment_mode":
                    self.do_set_deployment_mode(params)
                elif command == "context":
                    self.do_context(params)
                elif command == "help":
                    self.do_help()
                elif command == "exit" or command == "quit":
                    break
                else:
                    print("Invalid command: %s"%(command))
                    self.do_help()
            except EOFError:
                break  # Control-D pressed.
    
    def update_prompt(self):
        self.prompt = "[acc: {0}] [env: {1}] > ".format(self.account_id, self.environment_id)
    
    def do_set_deployment_mode(self, line):
        parser = BaseParser(prog="set_deployment_mode", description="Sets deployment mode")
        parser.add_argument("mode", choices=["readonly", "automatic"])
        
        args = parser.parse_args(line.split())
        if not args:
            return
        
        if not self.environment_id:
            print("context is required, run: context <account_id> <environment_id>")
            return
        
        if args.mode:
            result = api.sources_api.set_environment_deployment_mode(self.account_id, self.environment_id, args.mode)
            if result:
                print("ok")
            else:
                print("failed")
    
    def do_context(self, line):
        parser = BaseParser(prog="context", description="Sets context (account + environment)")
        parser.add_argument("account_id", type=str)
        parser.add_argument("environment_id", type=str)
        
        args = parser.parse_args(line.split())
        if not args: return
        
        if args.account_id and args.environment_id:
            self.account_id = args.account_id
            self.environment_id = args.environment_id
            self.update_prompt()
    
    def do_help(self):
        print (
            "\n=== Commands:\n\n"
            ":: *context*, *set_deployment_mode*, *exit*, *help*\n"
            "To get specific help type: COMMAND --help\n"
        )
ALCmd().run()
