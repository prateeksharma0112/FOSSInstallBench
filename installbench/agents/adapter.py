"""
Abstract interface defining how the framework communicates with AI software agents.
"""
from abc import ABC, abstractmethod
from typing import Any

from installbench.models.installation_task import InstallationTask
from installbench.sandbox.docker_manager import DockerManager


class AgentAdapter(ABC):
    """
    Base class for agent integrations.
    Any new agent evaluated by the framework must implement this interface.
    """
    
    @abstractmethod
    def invoke(
        self, 
        task: InstallationTask, 
        sandbox: DockerManager, 
        prompt: str
    ) -> dict[str, Any]:
        """
        Executes the agent against the provided task and sandbox.
        
        Args:
            task: The configuration and documentation for the installation.
            sandbox: The active Docker environment where the agent operates.
            prompt: The formatted instruction prompt.
            
        Returns:
            A dictionary containing raw execution results, including
            commands run, logs, and success state.
        """
        pass