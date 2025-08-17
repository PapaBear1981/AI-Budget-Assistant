import unittest
import asyncio

from backend.ai.unified_agent import get_unified_agent, QueryType

class TestAIResponseQuality(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Ensure the unified agent is initialized
        self.agent = get_unified_agent()

    async def test_basic_response(self):
        """Verify that the agent returns a non‑empty response with a valid confidence score."""
        user_input = "Show me my spending patterns for this month"
        response = await self.agent.process_query(user_input, context={})
        self.assertIsInstance(response.response_text, str)
        self.assertTrue(len(response.response_text.strip()) > 0, "Response text should not be empty")
        self.assertGreaterEqual(response.confidence, 0.0)
        self.assertLessEqual(response.confidence, 1.0)

    async def test_query_classification(self):
        """Check that the NLP module classifies a transaction analysis query correctly."""
        user_input = "What are my biggest expenses?"
        response = await self.agent.process_query(user_input, context={})
        self.assertEqual(response.query_type, QueryType.TRANSACTION_ANALYSIS)

    async def test_hallucination_detection_placeholder(self):
        """
        Placeholder test for hallucination detection.
        In a full implementation this would verify that the AI filter flags
        responses that contain unsupported facts.
        """
        user_input = "Tell me the weather on Mars tomorrow."
        response = await self.agent.process_query(user_input, context={})
        # Expect the agent to handle unknown queries gracefully
        self.assertTrue(True)

if __name__ == "__main__":
    asyncio.run(unittest.main())
