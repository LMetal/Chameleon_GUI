import pexpect
from typing import Optional
import re

class OpenStackShell:
    def __init__(self, openrc_path: str, password: str):
        self.openrc_path = openrc_path
        self.password = password
        self.shell = None
        self._initialize_shell()
    
    def _initialize_shell(self):
        try:
            self.shell = pexpect.spawn('/bin/bash', encoding='utf-8', timeout=30)
            self.shell.setecho(False)
            self.shell.delaybeforesend = 0.1
            
            self.shell.maxread = 50000
            
            unique_prompt = "OPENSTACK_SHELL>"
            self.shell.sendline(f'export PS1="{unique_prompt}"')
            self.shell.expect(unique_prompt, timeout=10)
            
            print(f"Sourcing: {self.openrc_path}")
            self.shell.sendline(f'source {self.openrc_path}')
            
            if self.password:
                index = self.shell.expect([
                    'Please enter your Chameleon CLI password:',
                    unique_prompt
                ], timeout=10)
                
                if index == 0:
                    self.shell.sendline(self.password)
                    self.shell.expect(unique_prompt, timeout=10)
            else:
                self.shell.expect(unique_prompt, timeout=10)
            
            print("Shell initialized successfully")
            
        except pexpect.TIMEOUT as e:
            raise Exception(f"Timeout during shell initialization: {e}")
        except Exception as e:
            raise Exception(f"Failed to initialize shell: {e}")
    
    def exec(self, command: str, timeout: int = 30) -> str:
        if self.shell is None or not self.shell.isalive():
            raise Exception("Shell is not active")
        
        try:
            #clear pending
            self.shell.expect_exact("OPENSTACK_SHELL>", timeout=1)
        except pexpect.TIMEOUT:
            pass
        
        print(f"Executing: {command}")
        
        #execute command
        self.shell.sendline(command)
        
        try:
            #comando eseguito
            self.shell.expect_exact("OPENSTACK_SHELL>", timeout=30)
            raw_output = self.shell.before
            
            output = self._clean_output(raw_output, command)
            
            error = self._has_error(output)
            if error:
                raise Exception(error)
            print(output)
            
            return output
            
        except pexpect.TIMEOUT:
            partial = self.shell.before if hasattr(self.shell, 'before') else ""
            raise Exception(
                f"Command '{command}' timed out after {timeout}s\n"
                f"Partial output: {partial[:500]}"
            )
    
    #ritorna l'output dell'esecuzione del comando pulito
    def _clean_output(self, raw_output, command):
        lines = raw_output.split('\n')
        cleaned_lines = []
        skip_first = True
        
        for line in lines:
            if skip_first and command in line:
                skip_first = False
                continue
            #filtra errori blazar
            if "blazarclient" in line:
                continue
            if line.strip():
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _has_error(self, output: str) -> bool:
        error_patterns = [
            r'failed',
            r'Failed',
            r'FAILED',
            r'Unable to',
            r'Could not',
            r'Permission denied',
            r'Connection refused'
        ]
        
        for line in output.splitlines():
            if any(re.search(ep, line, re.IGNORECASE) for ep in error_patterns):
                return line
        return False