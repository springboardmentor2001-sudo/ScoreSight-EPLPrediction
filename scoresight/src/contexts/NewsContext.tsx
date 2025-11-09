import React, { createContext, useContext, useReducer, ReactNode, useEffect } from 'react';
import { NewsState, NewsArticle, BlogPost } from '../types/news';

interface NewsContextType extends NewsState {
  fetchNews: () => Promise<void>;
  createBlog: (blogData: Partial<BlogPost>) => Promise<void>;
  likeArticle: (articleId: string) => void;
  toggleSavedArticle: (articleId: string) => void;
  setFilters: (filters: Partial<NewsState['filters']>) => void;
}

const NewsContext = createContext<NewsContextType | undefined>(undefined);

type NewsAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ARTICLES'; payload: NewsArticle[] }
  | { type: 'SET_USER_BLOGS'; payload: BlogPost[] }
  | { type: 'SET_FEATURED'; payload: NewsArticle }
  | { type: 'UPDATE_FILTERS'; payload: Partial<NewsState['filters']> }
  | { type: 'LIKE_ARTICLE'; payload: string }
  | { type: 'ADD_BLOG'; payload: BlogPost }
  | { type: 'TOGGLE_SAVED_ARTICLE'; payload: string }
  | { type: 'SET_SAVED_ARTICLES'; payload: string[] };

const newsReducer = (state: NewsState, action: NewsAction): NewsState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ARTICLES':
      return { ...state, articles: action.payload };
    case 'SET_USER_BLOGS':
      return { ...state, userBlogs: action.payload };
    case 'SET_FEATURED':
      return { ...state, featuredArticle: action.payload };
    case 'UPDATE_FILTERS':
      return { ...state, filters: { ...state.filters, ...action.payload } };
    case 'LIKE_ARTICLE':
      return {
        ...state,
        articles: state.articles.map(article =>
          article.id === action.payload
            ? { ...article, likes: article.likes + 1, isUserLiked: true }
            : article
        )
      };
    case 'ADD_BLOG':
      return {
        ...state,
        userBlogs: [action.payload, ...state.userBlogs]
      };
    case 'TOGGLE_SAVED_ARTICLE':
      const articleId = action.payload;
      const isCurrentlySaved = state.savedArticles.includes(articleId);
      return {
        ...state,
        savedArticles: isCurrentlySaved
          ? state.savedArticles.filter((id: string) => id !== articleId)
          : [...state.savedArticles, articleId]
      };
    case 'SET_SAVED_ARTICLES':
      return {
        ...state,
        savedArticles: action.payload
      };
    default:
      return state;
  }
};

// Helper function to determine category from title
const getCategoryFromTitle = (title: string): string => {
  if (!title) return 'general';
  
  const lowerTitle = title.toLowerCase();
  if (lowerTitle.includes('transfer') || lowerTitle.includes('sign') || lowerTitle.includes('deal')) {
    return 'transfer';
  } else if (lowerTitle.includes('injur') || lowerTitle.includes('fit') || lowerTitle.includes('recover')) {
    return 'injury';
  } else if (lowerTitle.includes('match') || lowerTitle.includes('fixture') || lowerTitle.includes('vs') || lowerTitle.includes('v ')) {
    return 'match';
  } else if (lowerTitle.includes('analysis') || lowerTitle.includes('tactic') || lowerTitle.includes('stats')) {
    return 'analysis';
  }
  return 'general';
};

const initialState: NewsState = {
  articles: [],
  userBlogs: [],
  featuredArticle: null,
  loading: false,
  filters: {
    category: 'all',
    type: 'all',
    sortBy: 'latest'
  },
  savedArticles: []
};

export const NewsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(newsReducer, initialState);

  // Load saved data from localStorage on component mount
  useEffect(() => {
    const savedBlogs = localStorage.getItem('userBlogs');
    if (savedBlogs) {
      dispatch({ type: 'SET_USER_BLOGS', payload: JSON.parse(savedBlogs) });
    }

    const savedArticles = localStorage.getItem('savedArticles');
    if (savedArticles) {
      dispatch({ type: 'SET_SAVED_ARTICLES', payload: JSON.parse(savedArticles) });
    }
  }, []);

  const fetchNews = async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const response = await fetch('http://localhost:8000/api/news/epl?limit=20');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.success && data.data && data.data.length > 0) {
        const articles: NewsArticle[] = data.data.map((item: any, index: number) => ({
          id: item.id || `news-${index}`,
          title: item.title || 'No title available',
          content: item.content || item.summary || '',
          excerpt: item.summary || 'Click to read more...',
          author: 'News Source',
          publishedAt: item.published || item.pubDate || new Date().toISOString(),
          source: item.source || 'Unknown Source',
          link: item.link,
          imageUrl: item.imageUrl,
          category: getCategoryFromTitle(item.title),
          type: 'news',
          likes: Math.floor(Math.random() * 100),
          comments: Math.floor(Math.random() * 50),
          isUserLiked: false
        }));

        dispatch({ type: 'SET_ARTICLES', payload: articles });
        
        if (articles.length > 0) {
          dispatch({ type: 'SET_FEATURED', payload: articles[0] });
        }
      } else {
        console.error('No data received from API:', data);
      }
      
    } catch (error) {
      console.error('Error fetching news:', error);
      dispatch({ type: 'SET_ARTICLES', payload: [] });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const createBlog = async (blogData: Partial<BlogPost>) => {
    try {
      const newBlog: BlogPost = {
        id: Date.now().toString(),
        title: blogData.title || 'Untitled Blog',
        content: blogData.content || '',
        excerpt: blogData.excerpt || (blogData.content ? blogData.content.substring(0, 150) + '...' : 'No content'),
        author: {
          id: 'user1',
          name: 'Current User'
        },
        publishedAt: new Date().toISOString(),
        tags: blogData.tags || [],
        likes: 0,
        comments: 0,
        isPublished: true
      };
      
      dispatch({ type: 'ADD_BLOG', payload: newBlog });
      
      // Save to localStorage
      const updatedBlogs = [newBlog, ...state.userBlogs];
      localStorage.setItem('userBlogs', JSON.stringify(updatedBlogs));
      
    } catch (error) {
      console.error('Error creating blog:', error);
      throw error;
    }
  };

  const likeArticle = (articleId: string) => {
    dispatch({ type: 'LIKE_ARTICLE', payload: articleId });
  };

  const toggleSavedArticle = (articleId: string) => {
    dispatch({ type: 'TOGGLE_SAVED_ARTICLE', payload: articleId });
    
    // Save to localStorage
    const updatedSavedArticles = state.savedArticles.includes(articleId)
      ? state.savedArticles.filter((id: string) => id !== articleId)
      : [...state.savedArticles, articleId];
    localStorage.setItem('savedArticles', JSON.stringify(updatedSavedArticles));
  };

  const setFilters = (filters: Partial<NewsState['filters']>) => {
    dispatch({ type: 'UPDATE_FILTERS', payload: filters });
  };

  return (
    <NewsContext.Provider value={{
      ...state,
      fetchNews,
      createBlog,
      likeArticle,
      toggleSavedArticle,
      setFilters
    }}>
      {children}
    </NewsContext.Provider>
  );
};

export const useNews = () => {
  const context = useContext(NewsContext);
  if (context === undefined) {
    throw new Error('useNews must be used within a NewsProvider');
  }
  return context;
};