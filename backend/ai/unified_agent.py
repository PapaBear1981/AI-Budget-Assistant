"""
Unified Financial Agent - Simplified AI Architecture
Single intelligent agent with modular capabilities for financial assistance
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from ..core.ai_security import get_ai_security_filter, get_privacy_manager
from ..core.security import get_audit_logger

# AI logging
ai_logger = logging.getLogger("unified_agent")
audit_logger = get_audit_logger()

class QueryType(Enum):
    """Types of financial queries the agent can handle"""
    TRANSACTION_ANALYSIS = "transaction_analysis"
    BUDGET_ADVICE = "budget_advice"
    SPENDING_INSIGHTS = "spending_insights"
    BILL_TRACKING = "bill_tracking"
    SAVINGS_RECOMMENDATIONS = "savings_recommendations"
    GENERAL_FINANCIAL = "general_financial"
    UNKNOWN = "unknown"

@dataclass
class AgentResponse:
    """Structured response from the unified agent"""
    response_text: str
    query_type: QueryType
    confidence: float
    data_used: List[str]
    recommendations: List[str]
    warnings: List[str]
    processing_time: float
    local_processing: bool

class FinancialAnalysisModule:
    """Module for financial data analysis and insights"""
    
    def __init__(self):
        self.analysis_patterns = {
            "spending_trends": ["trend", "pattern", "spending", "increase", "decrease"],
            "budget_variance": ["budget", "over", "under", "variance", "difference"],
            "category_analysis": ["category", "groceries", "entertainment", "utilities"],
            "anomaly_detection": ["unusual", "strange", "different", "anomaly", "outlier"]
        }
    
    async def analyze_spending_patterns(self, transactions: List[Dict[str, Any]], 
                                      user_query: str) -> Dict[str, Any]:
        """Analyze spending patterns from transaction data"""
        try:
            if not transactions:
                return {
                    "analysis": "No transaction data available for analysis",
                    "insights": [],
                    "recommendations": ["Start tracking your expenses to get insights"]
                }
            
            # Basic analysis for MVP
            total_spending = sum(t.get('amount', 0) for t in transactions if t.get('amount', 0) < 0)
            transaction_count = len(transactions)
            avg_transaction = total_spending / transaction_count if transaction_count > 0 else 0
            
            # Category breakdown
            categories = {}
            for transaction in transactions:
                category = transaction.get('category', 'Uncategorized')
                amount = abs(transaction.get('amount', 0))
                categories[category] = categories.get(category, 0) + amount
            
            # Generate insights
            insights = []
            recommendations = []
            
            if categories:
                top_category = max(categories, key=categories.get)
                insights.append(f"Your highest spending category is {top_category} (${categories[top_category]:.2f})")
                
                if categories[top_category] > abs(total_spending) * 0.4:
                    recommendations.append(f"Consider reviewing your {top_category} expenses - they represent a large portion of your spending")
            
            if transaction_count > 0:
                insights.append(f"You made {transaction_count} transactions with an average of ${abs(avg_transaction):.2f}")
            
            return {
                "analysis": f"Analyzed {transaction_count} transactions totaling ${abs(total_spending):.2f}",
                "insights": insights,
                "recommendations": recommendations,
                "categories": categories,
                "total_spending": abs(total_spending),
                "transaction_count": transaction_count
            }
            
        except Exception as e:
            ai_logger.error(f"Spending analysis failed: {str(e)}")
            return {
                "analysis": "Unable to analyze spending patterns at this time",
                "insights": [],
                "recommendations": ["Please try again later"]
            }

class BudgetAdvisoryModule:
    """Module for budget creation and optimization advice"""
    
    def __init__(self):
        self.budget_rules = {
            "50_30_20": {"needs": 0.5, "wants": 0.3, "savings": 0.2},
            "conservative": {"needs": 0.6, "wants": 0.2, "savings": 0.2},
            "aggressive_savings": {"needs": 0.5, "wants": 0.2, "savings": 0.3}
        }
    
    async def create_budget_recommendation(self, income: float, 
                                         current_expenses: Dict[str, float],
                                         user_query: str) -> Dict[str, Any]:
        """Create budget recommendations based on income and expenses"""
        try:
            if income <= 0:
                return {
                    "recommendation": "Please provide your monthly income to create a budget",
                    "budget_plan": {},
                    "advice": ["Track your income sources", "Consider all income streams"]
                }
            
            # Use 50/30/20 rule as default
            rule = self.budget_rules["50_30_20"]
            
            recommended_budget = {
                "Needs (Housing, Food, Transportation)": income * rule["needs"],
                "Wants (Entertainment, Dining Out)": income * rule["wants"],
                "Savings & Debt Payment": income * rule["savings"]
            }
            
            # Compare with current expenses if available
            advice = []
            if current_expenses:
                total_current = sum(current_expenses.values())
                if total_current > income:
                    advice.append("⚠️ Your current expenses exceed your income")
                    advice.append("Consider reducing discretionary spending")
                else:
                    savings_potential = income - total_current
                    advice.append(f"You have ${savings_potential:.2f} potential for savings")
            
            advice.extend([
                "Follow the 50/30/20 rule for balanced budgeting",
                "Prioritize building an emergency fund",
                "Review and adjust your budget monthly"
            ])
            
            return {
                "recommendation": f"Based on your ${income:.2f} monthly income, here's a recommended budget:",
                "budget_plan": recommended_budget,
                "advice": advice,
                "rule_used": "50/30/20 Rule"
            }
            
        except Exception as e:
            ai_logger.error(f"Budget recommendation failed: {str(e)}")
            return {
                "recommendation": "Unable to create budget recommendation at this time",
                "budget_plan": {},
                "advice": ["Please try again later"]
            }

class InsightsGeneratorModule:
    """Module for generating financial insights and reports"""
    
    async def generate_monthly_summary(self, transactions: List[Dict[str, Any]], 
                                     budget_data: Dict[str, Any],
                                     user_query: str) -> Dict[str, Any]:
        """Generate monthly financial summary"""
        try:
            current_month = datetime.now().strftime("%B %Y")
            
            if not transactions:
                return {
                    "summary": f"No transactions found for {current_month}",
                    "highlights": ["Start tracking your expenses to get insights"],
                    "action_items": ["Add your first transaction"]
                }
            
            # Calculate basic metrics
            total_income = sum(t.get('amount', 0) for t in transactions if t.get('amount', 0) > 0)
            total_expenses = abs(sum(t.get('amount', 0) for t in transactions if t.get('amount', 0) < 0))
            net_flow = total_income - total_expenses
            
            # Generate highlights
            highlights = [
                f"Total income: ${total_income:.2f}",
                f"Total expenses: ${total_expenses:.2f}",
                f"Net cash flow: ${net_flow:.2f}"
            ]
            
            # Generate action items
            action_items = []
            if net_flow < 0:
                action_items.append("⚠️ You spent more than you earned this month")
                action_items.append("Review your expenses and identify areas to cut back")
            elif net_flow > 0:
                action_items.append("✅ Great job! You had positive cash flow")
                action_items.append("Consider increasing your savings rate")
            
            if total_expenses > 0:
                action_items.append("Review your spending categories for optimization opportunities")
            
            return {
                "summary": f"Financial summary for {current_month}",
                "highlights": highlights,
                "action_items": action_items,
                "metrics": {
                    "total_income": total_income,
                    "total_expenses": total_expenses,
                    "net_flow": net_flow,
                    "transaction_count": len(transactions)
                }
            }
            
        except Exception as e:
            ai_logger.error(f"Monthly summary generation failed: {str(e)}")
            return {
                "summary": "Unable to generate monthly summary at this time",
                "highlights": [],
                "action_items": ["Please try again later"]
            }

class NLPProcessingModule:
    """Module for natural language processing and intent recognition"""
    
    def __init__(self):
        self.intent_keywords = {
            QueryType.TRANSACTION_ANALYSIS: [
                "transactions", "spending", "expenses", "purchases", "payments"
            ],
            QueryType.BUDGET_ADVICE: [
                "budget", "budgeting", "plan", "allocate", "distribute"
            ],
            QueryType.SPENDING_INSIGHTS: [
                "insights", "analysis", "patterns", "trends", "summary"
            ],
            QueryType.BILL_TRACKING: [
                "bills", "due", "payments", "utilities", "subscriptions"
            ],
            QueryType.SAVINGS_RECOMMENDATIONS: [
                "save", "savings", "invest", "emergency fund", "goals"
            ]
        }
    
    def classify_query(self, user_input: str) -> Tuple[QueryType, float]:
        """Classify user query and return intent with confidence"""
        try:
            user_input_lower = user_input.lower()
            scores = {}
            
            for query_type, keywords in self.intent_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in user_input_lower:
                        score += 1
                
                if score > 0:
                    scores[query_type] = score / len(keywords)
            
            if not scores:
                return QueryType.GENERAL_FINANCIAL, 0.5
            
            best_match = max(scores, key=scores.get)
            confidence = scores[best_match]
            
            return best_match, confidence
            
        except Exception as e:
            ai_logger.error(f"Query classification failed: {str(e)}")
            return QueryType.UNKNOWN, 0.0
    
    def extract_entities(self, user_input: str) -> Dict[str, Any]:
        """Extract relevant entities from user input"""
        entities = {}
        
        # Extract amounts (simple regex for MVP)
        import re
        amount_pattern = r'\$?(\d+(?:\.\d{2})?)'
        amounts = re.findall(amount_pattern, user_input)
        if amounts:
            entities['amounts'] = [float(amount) for amount in amounts]
        
        # Extract time periods
        time_patterns = {
            'month': r'\b(?:this month|last month|monthly)\b',
            'week': r'\b(?:this week|last week|weekly)\b',
            'year': r'\b(?:this year|last year|yearly|annual)\b'
        }
        
        for period, pattern in time_patterns.items():
            if re.search(pattern, user_input, re.IGNORECASE):
                entities['time_period'] = period
                break
        
        return entities

class UnifiedFinancialAgent:
    """
    Unified Financial Agent - Single intelligent agent for financial assistance
    Replaces complex multi-agent system with simplified modular approach
    """

    def __init__(self):
        # Initialize modules
        self.financial_analysis = FinancialAnalysisModule()
        self.budget_advisory = BudgetAdvisoryModule()
        self.insights_generator = InsightsGeneratorModule()
        self.nlp_processor = NLPProcessingModule()

        # Security components
        self.security_filter = get_ai_security_filter()
        self.privacy_manager = get_privacy_manager()

        # Agent state
        self.conversation_history = []
        self.user_context = {}

        ai_logger.info("UnifiedFinancialAgent initialized successfully")

    async def process_query(self, user_input: str, context: Dict[str, Any] = None,
                          user_id: str = "default") -> AgentResponse:
        """
        Main entry point for processing user queries
        """
        start_time = datetime.now()

        try:
            # Security: Sanitize input
            sanitized_input, input_warnings = await self.security_filter.sanitize_input(
                user_input, user_id
            )

            # Privacy: Check if local processing is needed (consult user consent if available)
            user_id_for_privacy = user_id if user_id and user_id != "default" else None
            use_local = await self.privacy_manager.should_use_local_processing(
                sanitized_input, context or {}, user_id=user_id_for_privacy
            )
            
            # If local processing selected, route to local LLM adapter
            if use_local:
                try:
                    from ..ai.local_llm import generate_local_response
                    local_resp = await generate_local_response(sanitized_input, context or {}, user_id_for_privacy)
                    
                    # Construct AgentResponse directly from local LLM
                    response = AgentResponse(
                        response_text=local_resp,
                        query_type=QueryType.GENERAL_FINANCIAL,
                        confidence=0.9,
                        data_used=[],
                        recommendations=[],
                        warnings=[],
                        processing_time=0.0,
                        local_processing=True
                    )
                    
                    # Filter output through security filter
                    filtered_response, output_warnings = await self.security_filter.filter_output(
                        response.response_text, user_id
                    )
                    response.response_text = filtered_response
                    response.warnings.extend(output_warnings)
                    
                    # Log and return early
                    audit_logger.log_security_event(
                        event_type="LOCAL_LLM_RESPONSE",
                        severity="INFO",
                        details={"user_id": user_id, "local_processing": True}
                    )
                    
                    return response
                except Exception as e:
                    ai_logger.error(f"Local LLM processing failed: {str(e)}")
                    # Fall through to normal processing if local LLM fails
                    pass

            # Anonymize context if using cloud processing
            if not use_local and context:
                context = await self.privacy_manager.anonymize_context(context)

            # Process the query
            response = await self._process_internal(sanitized_input, context or {}, user_id)

            # Security: Filter output
            filtered_response, output_warnings = await self.security_filter.filter_output(
                response.response_text, user_id
            )

            # Update response with filtered content and warnings
            response.response_text = filtered_response
            response.warnings.extend(input_warnings + output_warnings)
            response.local_processing = use_local
            response.processing_time = (datetime.now() - start_time).total_seconds()

            # Log for audit
            audit_logger.log_security_event(
                event_type="AI_QUERY_PROCESSED",
                severity="INFO",
                details={
                    "user_id": user_id,
                    "query_type": response.query_type.value,
                    "confidence": response.confidence,
                    "local_processing": use_local,
                    "processing_time": response.processing_time,
                    "warnings_count": len(response.warnings)
                }
            )

            return response

        except Exception as e:
            ai_logger.error(f"Query processing failed: {str(e)}")
            audit_logger.log_security_event(
                event_type="AI_QUERY_FAILED",
                severity="ERROR",
                details={"user_id": user_id, "error": str(e)}
            )

            # Return safe error response
            return AgentResponse(
                response_text="I'm sorry, I'm unable to process your request at the moment. Please try again later.",
                query_type=QueryType.UNKNOWN,
                confidence=0.0,
                data_used=[],
                recommendations=["Please try rephrasing your question"],
                warnings=["Processing error occurred"],
                processing_time=(datetime.now() - start_time).total_seconds(),
                local_processing=True
            )

    async def _process_internal(self, user_input: str, context: Dict[str, Any],
                              user_id: str) -> AgentResponse:
        """Internal query processing logic"""

        # Classify the query
        query_type, confidence = self.nlp_processor.classify_query(user_input)

        # Extract entities
        entities = self.nlp_processor.extract_entities(user_input)

        # Route to appropriate module based on query type
        if query_type == QueryType.TRANSACTION_ANALYSIS:
            result = await self._handle_transaction_analysis(user_input, context, entities)
        elif query_type == QueryType.BUDGET_ADVICE:
            result = await self._handle_budget_advice(user_input, context, entities)
        elif query_type == QueryType.SPENDING_INSIGHTS:
            result = await self._handle_spending_insights(user_input, context, entities)
        elif query_type == QueryType.SAVINGS_RECOMMENDATIONS:
            result = await self._handle_savings_recommendations(user_input, context, entities)
        else:
            result = await self._handle_general_financial(user_input, context, entities)

        return AgentResponse(
            response_text=result.get("response", "I'm here to help with your financial questions."),
            query_type=query_type,
            confidence=confidence,
            data_used=result.get("data_used", []),
            recommendations=result.get("recommendations", []),
            warnings=[],
            processing_time=0.0,  # Will be set by caller
            local_processing=False  # Will be set by caller
        )

    async def _handle_transaction_analysis(self, user_input: str, context: Dict[str, Any],
                                         entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transaction analysis queries"""
        transactions = context.get("transactions", [])

        analysis = await self.financial_analysis.analyze_spending_patterns(
            transactions, user_input
        )

        response_text = f"{analysis['analysis']}\n\n"

        if analysis['insights']:
            response_text += "📊 **Key Insights:**\n"
            for insight in analysis['insights']:
                response_text += f"• {insight}\n"

        if analysis['recommendations']:
            response_text += "\n💡 **Recommendations:**\n"
            for rec in analysis['recommendations']:
                response_text += f"• {rec}\n"

        return {
            "response": response_text,
            "data_used": ["transactions"],
            "recommendations": analysis['recommendations']
        }

    async def _handle_budget_advice(self, user_input: str, context: Dict[str, Any],
                                  entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle budget advice queries"""
        income = context.get("monthly_income", 0)
        expenses = context.get("current_expenses", {})

        # Try to extract income from entities if not in context
        if income == 0 and "amounts" in entities:
            income = max(entities["amounts"])  # Assume largest amount is income

        advice = await self.budget_advisory.create_budget_recommendation(
            income, expenses, user_input
        )

        response_text = f"{advice['recommendation']}\n\n"

        if advice['budget_plan']:
            response_text += "💰 **Recommended Budget:**\n"
            for category, amount in advice['budget_plan'].items():
                response_text += f"• {category}: ${amount:.2f}\n"

        if advice['advice']:
            response_text += "\n📋 **Budget Tips:**\n"
            for tip in advice['advice']:
                response_text += f"• {tip}\n"

        return {
            "response": response_text,
            "data_used": ["income", "expenses"],
            "recommendations": advice['advice']
        }

    async def _handle_spending_insights(self, user_input: str, context: Dict[str, Any],
                                      entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle spending insights queries"""
        transactions = context.get("transactions", [])
        budget_data = context.get("budget", {})

        insights = await self.insights_generator.generate_monthly_summary(
            transactions, budget_data, user_input
        )

        response_text = f"📈 **{insights['summary']}**\n\n"

        if insights['highlights']:
            response_text += "🔍 **Highlights:**\n"
            for highlight in insights['highlights']:
                response_text += f"• {highlight}\n"

        if insights['action_items']:
            response_text += "\n✅ **Action Items:**\n"
            for action in insights['action_items']:
                response_text += f"• {action}\n"

        return {
            "response": response_text,
            "data_used": ["transactions", "budget"],
            "recommendations": insights['action_items']
        }

    async def _handle_savings_recommendations(self, user_input: str, context: Dict[str, Any],
                                            entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle savings recommendation queries"""
        # Simple savings advice for MVP
        recommendations = [
            "Start with an emergency fund of 3-6 months of expenses",
            "Automate your savings to make it consistent",
            "Look for high-yield savings accounts",
            "Consider the 50/30/20 budgeting rule",
            "Review and reduce unnecessary subscriptions"
        ]

        response_text = "💰 **Savings Recommendations:**\n\n"
        for i, rec in enumerate(recommendations, 1):
            response_text += f"{i}. {rec}\n"

        response_text += "\n💡 **Pro Tip:** Start small and increase your savings rate gradually as you build the habit."

        return {
            "response": response_text,
            "data_used": [],
            "recommendations": recommendations
        }

    async def _handle_general_financial(self, user_input: str, context: Dict[str, Any],
                                      entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general financial queries"""
        response_text = """I'm your AI financial assistant! I can help you with:

📊 **Transaction Analysis** - "Show me my spending patterns"
💰 **Budget Planning** - "Help me create a budget"
📈 **Financial Insights** - "Give me a monthly summary"
💡 **Savings Advice** - "How can I save more money?"

What would you like to know about your finances?"""

        return {
            "response": response_text,
            "data_used": [],
            "recommendations": [
                "Try asking about your spending patterns",
                "Ask for budget advice",
                "Request a financial summary"
            ]
        }

# Global agent instance
unified_agent = UnifiedFinancialAgent()

def get_unified_agent() -> UnifiedFinancialAgent:
    """Get global unified financial agent instance"""
    return unified_agent
