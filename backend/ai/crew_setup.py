"""
CrewAI Framework Setup and Configuration
Initializes the multi-agent system for AI Budget Assistant
"""

import os
from typing import Dict, Any, Optional
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from .agents.financial_analyst import FinancialAnalystAgent
from .agents.transaction_processor import TransactionProcessorAgent
from .agents.budget_advisor import BudgetAdvisorAgent
from .agents.insights_generator import InsightsGeneratorAgent
from .agents.query_handler import QueryHandlerAgent

# Load environment variables
load_dotenv()

class CrewAIManager:
    """Manages the CrewAI multi-agent system for financial assistance."""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.agents: Dict[str, Agent] = {}
        self.crew: Optional[Crew] = None
        self._initialize_agents()
        self._setup_crew()
    
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the LLM for agent communication."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        return ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,  # Low temperature for consistent financial advice
            api_key=api_key
        )
    
    def _initialize_agents(self):
        """Initialize all specialized agents."""
        
        # Financial Analyst Agent
        self.agents["financial_analyst"] = Agent(
            role="Financial Data Analyst",
            goal="Analyze financial data, identify trends, detect anomalies, and provide insights",
            backstory="""You are an expert financial analyst with deep knowledge of personal 
            finance patterns, spending behaviors, and financial health indicators. You excel 
            at identifying unusual spending patterns, trends, and opportunities for optimization.""",
            tools=FinancialAnalystAgent.get_tools(),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Transaction Processor Agent
        self.agents["transaction_processor"] = Agent(
            role="Transaction Processing Specialist",
            goal="Process, categorize, and validate financial transactions with high accuracy",
            backstory="""You are a meticulous transaction processing expert who specializes 
            in categorizing financial transactions, detecting duplicates, and ensuring data 
            accuracy. You understand various transaction formats and can intelligently 
            categorize expenses based on merchant names, amounts, and patterns.""",
            tools=TransactionProcessorAgent.get_tools(),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Budget Advisor Agent
        self.agents["budget_advisor"] = Agent(
            role="Personal Budget Advisor",
            goal="Create, optimize, and manage budgets while providing personalized financial advice",
            backstory="""You are a certified financial planner with expertise in personal 
            budgeting, goal setting, and financial optimization. You help users create 
            realistic budgets, set achievable financial goals, and provide actionable 
            advice for improving their financial health.""",
            tools=BudgetAdvisorAgent.get_tools(),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Insights Generator Agent
        self.agents["insights_generator"] = Agent(
            role="Financial Insights Specialist",
            goal="Generate comprehensive financial reports, summaries, and actionable insights",
            backstory="""You are a financial insights expert who excels at creating 
            clear, actionable reports and summaries. You can identify key financial 
            patterns, generate 'What Changed?' analyses, and provide forecasting 
            insights that help users understand their financial trajectory.""",
            tools=InsightsGeneratorAgent.get_tools(),
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Query Handler Agent (Master Coordinator)
        self.agents["query_handler"] = Agent(
            role="AI Assistant Coordinator",
            goal="Understand user queries, coordinate agent responses, and provide unified assistance",
            backstory="""You are the master coordinator of the AI Budget Assistant system. 
            You understand natural language queries about personal finance, coordinate 
            with specialized agents to gather information, and provide clear, helpful 
            responses to users. You maintain conversation context and ensure responses 
            are accurate and actionable.""",
            tools=QueryHandlerAgent.get_tools(),
            llm=self.llm,
            verbose=True,
            allow_delegation=True  # Can delegate to other agents
        )
    
    def _setup_crew(self):
        """Setup the CrewAI crew with agents and process configuration."""
        agent_list = list(self.agents.values())
        
        self.crew = Crew(
            agents=agent_list,
            process=Process.hierarchical,  # Query handler coordinates others
            manager_llm=self.llm,
            verbose=True,
            memory=True,  # Enable conversation memory
            max_iter=3,  # Limit iterations to prevent infinite loops
            max_execution_time=30  # 30 second timeout for responses
        )
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Process a user query through the CrewAI system."""
        if not self.crew:
            raise RuntimeError("CrewAI system not initialized")
        
        # Create a task for the query
        task = Task(
            description=f"""
            Process the following user query about their personal finances:
            
            Query: {query}
            
            Context: {context or {}}
            
            Provide a helpful, accurate, and actionable response. If you need to 
            gather data or perform analysis, coordinate with the appropriate 
            specialized agents. Ensure your response is clear and addresses 
            the user's specific question or request.
            """,
            agent=self.agents["query_handler"],
            expected_output="A clear, helpful response to the user's financial query"
        )
        
        # Execute the task
        result = self.crew.kickoff(tasks=[task])
        return result
    
    def get_agent_status(self) -> Dict[str, str]:
        """Get the status of all agents."""
        return {
            name: "active" if agent else "inactive" 
            for name, agent in self.agents.items()
        }

# Global CrewAI manager instance
crew_manager: Optional[CrewAIManager] = None

async def initialize_crew() -> CrewAIManager:
    """Initialize the global CrewAI manager."""
    global crew_manager
    if crew_manager is None:
        crew_manager = CrewAIManager()
    return crew_manager

async def get_crew_manager() -> CrewAIManager:
    """Get the global CrewAI manager instance."""
    if crew_manager is None:
        raise RuntimeError("CrewAI system not initialized. Call initialize_crew() first.")
    return crew_manager
