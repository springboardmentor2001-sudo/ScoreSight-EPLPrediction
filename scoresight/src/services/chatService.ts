// Mock AI service - replace with real OpenAI API later
export const getAIResponse = async (userMessage: string): Promise<string> => {
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  const lowerMessage = userMessage.toLowerCase();
  
  if (lowerMessage.includes('why') && lowerMessage.includes('predict')) {
    return "Our prediction is based on team form, head-to-head records, and home advantage. The home team has won 4 of their last 5 matches.";
  }
  
  if (lowerMessage.includes('compare')) {
    return "Manchester City has better attack (92/100) while Liverpool has stronger defense (88/100). City's home form gives them the edge.";
  }
  
  if (lowerMessage.includes('bet')) {
    return "Based on our analysis, Both Teams to Score has good value with 68% probability.";
  }
  
  return "I can help explain predictions, compare teams, or analyze match statistics. What would you like to know?";
};

export const quickQuestions = [
  {
    id: '1',
    question: 'Explain Man City vs Liverpool prediction',
    category: 'predictions'
  },
  {
    id: '2',
    question: 'Compare Arsenal and Tottenham',
    category: 'teams'
  },
  {
    id: '3', 
    question: 'Best betting value this weekend?',
    category: 'betting'
  }
];