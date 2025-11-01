# chatbot_service.py
import os
import requests
import json
import asyncio
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MultiAIProvider:
    """Handles multiple AI providers with proper API configurations"""
    
    def __init__(self):
        self.providers = [
            self._try_groq,    # First try Groq (free & fast)
            self._try_gemini,  # Then try Gemini
            self._try_deepseek # Finally try DeepSeek
        ]
        self.setup_providers()
    
    def setup_providers(self):
        """Check which providers are available"""
        self.available_providers = []
        
        if os.getenv('GROQ_API_KEY') and os.getenv('GROQ_API_KEY') != 'your_actual_groq_key_here':
            self.available_providers.append('Groq')
            print("✅ Groq API configured")
        
        if os.getenv('GEMINI_API_KEY'):
            self.available_providers.append('Gemini')
            print("✅ Gemini API configured")
        
        if os.getenv('DEEPSEEK_API_KEY'):
            self.available_providers.append('DeepSeek')
            print("✅ DeepSeek API configured")
        
        print(f"🎯 Available AI providers: {self.available_providers}")
    
    async def ask_question(self, question: str) -> str:
        """Try all available AI providers until one works"""
        # First try using ML models for football-specific questions
        from main import predict_match_internal, team_analyzer
        
        if any(term.lower() in question.lower() for term in ['epl', 'premier league', 'football', 'soccer']):
            # Check for team names in the question
            all_teams = team_analyzer.get_all_trained_teams()
            mentioned_teams = [team for team in all_teams if team.lower() in question.lower()]

            if len(mentioned_teams) >= 2:
                # Try prediction
                try:
                    prediction = await predict_match_internal(mentioned_teams[0], mentioned_teams[1])
                    if 'error' not in prediction:
                        return f"""Based on our ML model analysis for {mentioned_teams[0]} vs {mentioned_teams[1]}:
- Home Win: {prediction['home_win_prob']:.1%}
- Draw: {prediction['draw_prob']:.1%}
- Away Win: {prediction['away_win_prob']:.1%}
Predicted outcome: {prediction['predicted_outcome']} ({prediction['predicted_score']})"""
                except Exception as e:
                    print(f"ML prediction failed: {e}")

            elif len(mentioned_teams) == 1:
                # Try team analysis
                try:
                    team_stats = team_analyzer.get_team_analysis(mentioned_teams[0])
                    if 'error' not in team_stats:
                        return f"""Here's the analysis for {mentioned_teams[0]}:
- Overall Strength: {team_stats['overall_strength']}/100
- Recent Form: {' '.join(team_stats['recent_form'])}
- Win Rate: {team_stats['win_percentage']}%

{team_stats['analysis']}"""
                except Exception as e:
                    print(f"Team analysis failed: {e}")

        # If ML models don't have an answer, try AI providers
        if not self.available_providers:
            return "I apologize, but I couldn't find specific information about that. Let me provide some general football knowledge: EPL stands for English Premier League, which is England's top professional football division. It was founded in 1992 and is one of the most watched sports leagues globally."
        
        for provider in self.providers:
            try:
                response = await provider(question)
                if response and response != "SERVICE_UNAVAILABLE":
                    return response
            except Exception as e:
                print(f"❌ Provider failed: {e}")
                continue
        
        # Final fallback - provide general football knowledge
        return """I apologize for not being able to connect to AI services at the moment, but I can help with general football knowledge. 

The English Premier League (EPL) is England's top professional football league and features 20 teams competing for the title each season. Teams play 38 matches (home and away against each team), with 3 points awarded for a win and 1 for a draw. The team with the most points at the end of the season wins the league.

Feel free to ask about specific teams, match predictions, or historical data, and I'll try to help using our statistical models and historical database."""
    
    async def _try_groq(self, question: str) -> str:
        """Try Groq API - Updated with current models"""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key or api_key == 'your_actual_groq_key_here':
            return "SERVICE_UNAVAILABLE"
        
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Football expert prompt
            prompt = f"""You are Scoresight, a football expert assistant specializing in Premier League analysis. 
Provide accurate, detailed information about football rules, history, teams, players, and statistics.

User Question: {question}

Please provide a comprehensive but concise answer focused on football knowledge.
If the question is not about football, politely explain you specialize in football topics.

Answer in a helpful, engaging tone:"""

            # Updated model list - using current available models
            payload = {
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are a football expert assistant for Scoresight. Provide accurate information about Premier League, football rules, history, teams, players, and statistics."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "model": "llama-3.1-8b-instant",  # Updated model - currently available
                "temperature": 0.3,
                "max_tokens": 1000,
                "stream": False
            }
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers, 
                    json=payload, 
                    timeout=30
                )
            )
            
            print(f"🔧 Groq API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                print(f"❌ Groq API error {response.status_code}: {response.text}")
                
                # If model not found, try alternative models
                if "model" in response.text.lower() and "not found" in response.text.lower():
                    return await self._try_groq_alternative(question, api_key)
                
                return "SERVICE_UNAVAILABLE"
                
        except Exception as e:
            print(f"❌ Groq API failed: {e}")
            return "SERVICE_UNAVAILABLE"
    
    async def _try_groq_alternative(self, question: str, api_key: str) -> str:
        """Try alternative Groq models"""
        alternative_models = [
            "llama-3.1-8b-instant",
            "llama3-8b-8192",  # Try original one more time
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]
        
        for model in alternative_models:
            try:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "messages": [{"role": "user", "content": question}],
                    "model": model,
                    "temperature": 0.3,
                    "max_tokens": 500
                }
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers, 
                        json=payload, 
                        timeout=20
                    )
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Groq model {model} worked!")
                    return data['choices'][0]['message']['content']
                else:
                    print(f"❌ Groq model {model} failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Groq model {model} error: {e}")
                continue
        
        return "SERVICE_UNAVAILABLE"
    
    async def _try_gemini(self, question: str) -> str:
        """Try Gemini API with correct endpoint"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return "SERVICE_UNAVAILABLE"
        
        try:
            # Updated Gemini API endpoint
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"""You are a football expert assistant. Answer this question accurately and concisely:

Question: {question}

Provide detailed football information if relevant, otherwise politely decline."""
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 1000
                }
            }
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.post(url, json=payload, timeout=30)
            )
            
            print(f"🔧 Gemini API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    return "SERVICE_UNAVAILABLE"
            else:
                print(f"❌ Gemini API error {response.status_code}: {response.text}")
                
                # Try alternative Gemini endpoint
                return await self._try_gemini_alternative(question, api_key)
                
        except Exception as e:
            print(f"❌ Gemini API failed: {e}")
            return "SERVICE_UNAVAILABLE"
    
    async def _try_gemini_alternative(self, question: str, api_key: str) -> str:
        """Try alternative Gemini endpoint"""
        try:
            # Alternative endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"Answer: {question}"}]
                }]
            }
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.post(url, json=payload, timeout=20)
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    return data['candidates'][0]['content']['parts'][0]['text']
            
            return "SERVICE_UNAVAILABLE"
            
        except Exception as e:
            print(f"❌ Gemini alternative failed: {e}")
            return "SERVICE_UNAVAILABLE"
    
    async def _try_deepseek(self, question: str) -> str:
        """Try DeepSeek API"""
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            return "SERVICE_UNAVAILABLE"
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            prompt = f"""You are a football expert. Answer this question: {question}"""
            
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 1000,
                "stream": False
            }
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers, 
                    json=payload, 
                    timeout=30
                )
            )
            
            print(f"🔧 DeepSeek API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                print(f"❌ DeepSeek API error {response.status_code}: {response.text}")
                return "SERVICE_UNAVAILABLE"
                
        except Exception as e:
            print(f"❌ DeepSeek API failed: {e}")
            return "SERVICE_UNAVAILABLE"

class ChatbotService:
    """Main chatbot service with ML-first approach"""
    
    def __init__(self):
        self.ai_provider = MultiAIProvider()
        self.epl_teams = self.get_all_trained_teams()
        
        # Keywords for routing
        self.prediction_keywords = ['predict', 'forecast', 'who will win', 'outcome', 'probability']
        self.team_keywords = ['stats', 'form', 'performance', 'record', 'analysis', 'strength']
        self.h2h_keywords = ['head to head', 'h2h', 'history', 'against', 'vs']
        
        print("✅ Chatbot Service initialized with API support!")
    
    def get_all_trained_teams(self):
        """Get all unique teams from training data"""
        return [
            'Arsenal', 'Aston Villa', 'Birmingham', 'Blackburn', 'Blackpool',
            'Bolton', 'Bournemouth', 'Bradford', 'Brentford', 'Brighton',
            'Burnley', 'Cardiff', 'Charlton', 'Chelsea', 'Coventry', 
            'Crystal Palace', 'Derby', 'Everton', 'Fulham', 'Huddersfield',
            'Hull', 'Ipswich', 'Leeds', 'Leicester', 'Liverpool',
            'Man City', 'Man United', 'Middlesbrough', 'Newcastle', 'Norwich',
            'Portsmouth', 'QPR', 'Reading', 'Sheffield United', 'Southampton',
            'Stoke', 'Sunderland', 'Swansea', 'Tottenham', 'Watford',
            'West Brom', 'West Ham', 'Wigan', 'Wolves', "Nott'm Forest"
        ]
    
    def classify_question(self, question: str) -> str:
        """Classify the type of question"""
        question_lower = question.lower()
        
        if any(keyword in question_lower for keyword in self.prediction_keywords):
            return 'prediction'
        if any(keyword in question_lower for keyword in self.team_keywords):
            return 'team_analysis'
        if any(keyword in question_lower for keyword in self.h2h_keywords):
            return 'head_to_head'
        if any(team.lower() in question_lower for team in self.epl_teams):
            return 'epl_specific'
        
        return 'general'
    
    def extract_teams(self, question: str) -> List[str]:
        """Extract team names from question"""
        question_lower = question.lower()
        found_teams = []
        
        for team in self.epl_teams:
            if team.lower() in question_lower:
                found_teams.append(team)
        
        return found_teams
    
    async def process_question(self, question: str) -> Dict[str, Any]:
        """Process question: Try ML models first, then AI as fallback"""
        try:
            print(f"🤖 Processing: '{question}'")
            
            # Classify question
            question_type = self.classify_question(question)
            teams = self.extract_teams(question)
            
            print(f"📊 Type: {question_type}, Teams: {teams}")
            
            # STEP 1: Try ML Models and Team Analyzer FIRST
            ml_response = await self._try_ml_models(question, question_type, teams)
            if ml_response:
                print("✅ Using ML model response")
                return ml_response
            
            # STEP 2: If ML models can't handle it, use AI as FALLBACK
            print("🔄 Falling back to AI provider")
            ai_response = await self.ai_provider.ask_question(question)
            
            return {
                "source": "ai_fallback",
                "response": ai_response,
                "confidence": "medium",
                "data": {"question_type": question_type, "teams": teams}
            }
                
        except Exception as e:
            print(f"🔴 Error: {e}")
            return {
                "source": "error",
                "response": "I apologize, but I encountered an error. Please try again.",
                "confidence": "low",
                "data": None
            }
    
    async def _try_ml_models(self, question: str, question_type: str, teams: List[str]) -> Dict[str, Any]:
        """Try to get response from ML models and team analyzer first"""
        try:
            from main import predict_match_internal, team_analyzer
            
            # 1. PREDICTION QUESTIONS
            if question_type == 'prediction' and len(teams) >= 2:
                prediction_result = await predict_match_internal(teams[0], teams[1])
                if 'error' not in prediction_result:
                    response_text = f"""
🔮 **Match Prediction: {teams[0]} vs {teams[1]}**

🏆 **Probabilities:**
• Home Win: {prediction_result['home_win_prob']:.1%}
• Draw: {prediction_result['draw_prob']:.1%}  
• Away Win: {prediction_result['away_win_prob']:.1%}

📊 **Predicted Outcome:** {prediction_result['predicted_outcome']}
🎯 **Confidence:** {prediction_result['confidence'].upper()}
📈 **Predicted Score:** {prediction_result['predicted_score']}

💡 **Key Factors:**
{chr(10).join(['• ' + factor for factor in prediction_result['keyFactors']])}

🤖 *Using Scoresight ML Model (75% accuracy)*
"""
                    return {
                        "source": "ml_model",
                        "response": response_text,
                        "confidence": "high",
                        "data": prediction_result
                    }
            
            # 2. TEAM ANALYSIS QUESTIONS
            elif question_type == 'team_analysis' and len(teams) >= 1:
                team_stats = team_analyzer.get_team_analysis(teams[0])
                if 'error' not in team_stats:
                    response_text = f"""
📊 **Team Analysis: {teams[0]}**

🏆 **Overall Strength:** {team_stats.get('overall_strength', 'N/A')}/100
⚽ **Attack Rating:** {team_stats.get('attack_strength', 'N/A')}/100
🛡️ **Defense Rating:** {team_stats.get('defense_strength', 'N/A')}/100

📈 **Recent Form:** {' '.join(team_stats.get('recent_form', []))}
🎯 **Win Percentage:** {team_stats.get('win_percentage', 'N/A')}%

📋 **Performance Analysis:**
{team_stats.get('analysis', 'No analysis available.')}
"""
                    return {
                        "source": "team_analyzer", 
                        "response": response_text,
                        "confidence": "high",
                        "data": team_stats
                    }
            
            # 3. HEAD-TO-HEAD QUESTIONS
            elif question_type == 'head_to_head' and len(teams) >= 2:
                h2h = team_analyzer.get_head_to_head(teams[0], teams[1])
                if h2h.get('total_matches', 0) > 0:
                    response_text = f"""
🤝 **Head-to-Head: {teams[0]} vs {teams[1]}**

📊 **Total Matches:** {h2h['total_matches']}
🏆 **{teams[0]} Wins:** {h2h['team1_wins']} ({h2h['team1_win_percentage']}%)
🏆 **{teams[1]} Wins:** {h2h['team2_wins']} ({h2h['team2_win_percentage']}%)
⚖️ **Draws:** {h2h['draws']} ({h2h['draw_percentage']}%)
"""
                    return {
                        "source": "team_analyzer",
                        "response": response_text,
                        "confidence": "high",
                        "data": h2h
                    }
            
            return None  # ML models can't handle this question
                
        except Exception as e:
            print(f"🔴 ML models error: {e}")
            return None

# Global instance
chatbot_service = ChatbotService()