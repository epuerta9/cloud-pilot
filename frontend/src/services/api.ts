import { Message, StructuredContent } from '../types';

// Mock delay function
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Mock API service
export const ApiService = {
  // Simulate streaming response
  async streamResponse(query: string, 
    onMessageUpdate: (content: string) => void, 
    onComplete: (message: Message) => void
  ): Promise<void> {
    // Initial empty content
    let content = '';
    
    // Generate mock response based on query
    const fullResponse = getMockResponse(query);
    const structuredContent = generateMockStructuredContent(query);
    
    // Simulate streaming by adding chunks of text
    const words = fullResponse.split(' ');
    
    for (let i = 0; i < words.length; i++) {
      // Add next word with space
      content += (i === 0 ? '' : ' ') + words[i];
      
      // Update with current content
      onMessageUpdate(content);
      
      // Random delay between 50-150ms
      await delay(Math.random() * 100 + 50);
    }
    
    // Complete message with structured content
    const message: Message = {
      id: Date.now().toString(),
      role: 'assistant',
      content: fullResponse,
      timestamp: new Date(),
      structuredContent
    };
    
    // Small delay before completing
    await delay(300);
    
    // Call complete callback
    onComplete(message);
  }
};

// Mock response generator
const getMockResponse = (query: string): string => {
  // Simple mock responses based on keywords
  if (query.toLowerCase().includes('hello') || query.toLowerCase().includes('hi')) {
    return "Hello! I'm Cloud Pilot, your AI assistant. How can I help you today?";
  } else if (query.toLowerCase().includes('help')) {
    return "I can help you with coding questions, explain concepts, generate code, or just chat about technology. What would you like to know?";
  } else if (query.toLowerCase().includes('code') || query.toLowerCase().includes('function')) {
    return "```javascript\n// Here's a sample function\nfunction greet(name) {\n  return 'Hello, ' + name + '!';\n}\n\n// Usage\nconst message = greet('User');\nconsole.log(message); // Outputs: Hello, User!\n```";
  } else if (query.toLowerCase().includes('thanks') || query.toLowerCase().includes('thank you')) {
    return "You're welcome! Feel free to ask if you need anything else.";
  } else {
    return "I understand you're asking about '" + query + "'. In a real implementation, I would connect to an AI API to provide a helpful response. For now, this is a placeholder response.";
  }
};

// Generate mock structured content
const generateMockStructuredContent = (query: string): StructuredContent => {
  // Simple mock structured content based on keywords
  if (query.toLowerCase().includes('code') || query.toLowerCase().includes('function')) {
    return {
      title: "Code Example: JavaScript Function",
      sections: [
        {
          type: 'heading',
          content: 'JavaScript Function Example',
          metadata: { level: 1 }
        },
        {
          type: 'text',
          content: 'Here is a sample JavaScript function that demonstrates basic functionality:'
        },
        {
          type: 'code',
          content: `function greet(name) {\n  return 'Hello, ' + name + '!';\n}\n\n// Usage\nconst message = greet('User');\nconsole.log(message); // Outputs: Hello, User!`,
          metadata: { language: 'javascript' }
        },
        {
          type: 'heading',
          content: 'How It Works',
          metadata: { level: 2 }
        },
        {
          type: 'text',
          content: 'The function takes a name parameter and returns a greeting string. Here\'s a breakdown of the steps:'
        },
        {
          type: 'list',
          content: [
            'Define a function named "greet" that accepts one parameter',
            'Concatenate strings to form a greeting',
            'Return the result from the function',
            'Call the function with an argument',
            'Log the result to the console'
          ]
        }
      ]
    };
  } else if (query.toLowerCase().includes('react') || query.toLowerCase().includes('hooks')) {
    return {
      title: "React Hooks Overview",
      sections: [
        {
          type: 'heading',
          content: 'Understanding React Hooks',
          metadata: { level: 1 }
        },
        {
          type: 'text',
          content: 'React Hooks are functions that let you "hook into" React state and lifecycle features from function components.'
        },
        {
          type: 'heading',
          content: 'Common Hooks',
          metadata: { level: 2 }
        },
        {
          type: 'table',
          content: [
            { Hook: 'useState', Purpose: 'State management in functional components' },
            { Hook: 'useEffect', Purpose: 'Side effects in functional components' },
            { Hook: 'useContext', Purpose: 'Access context in functional components' },
            { Hook: 'useRef', Purpose: 'Create mutable references' },
            { Hook: 'useReducer', Purpose: 'Complex state management with reducer pattern' }
          ]
        },
        {
          type: 'heading',
          content: 'useState Example',
          metadata: { level: 2 }
        },
        {
          type: 'code',
          content: `import React, { useState } from 'react';\n\nfunction Counter() {\n  const [count, setCount] = useState(0);\n\n  return (\n    <div>\n      <p>You clicked {count} times</p>\n      <button onClick={() => setCount(count + 1)}>\n        Click me\n      </button>\n    </div>\n  );\n}`,
          metadata: { language: 'jsx' }
        }
      ]
    };
  } else {
    return {
      title: "Default Response",
      sections: [
        {
          type: 'heading',
          content: 'Information',
          metadata: { level: 1 }
        },
        {
          type: 'text',
          content: 'In a real implementation, this would contain structured content based on your query. For now, this is a placeholder response.'
        },
        {
          type: 'text',
          content: 'The document view can display various types of content including headings, paragraphs, code blocks, lists, and tables.'
        }
      ]
    };
  }
}; 