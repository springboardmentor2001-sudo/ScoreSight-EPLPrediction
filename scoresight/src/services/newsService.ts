import { NewsArticle, BlogPost } from '../types/news';

class NewsService {
  private baseUrl = 'http://localhost:8000/api/news';

  // Get latest news from backend
  async getLatestNews(limit: number = 20): Promise<NewsArticle[]> {
    try {
      const response = await fetch(`${this.baseUrl}/epl?limit=${limit}`);
      if (!response.ok) throw new Error('Failed to fetch news');
      
      const data = await response.json();
      return data.success ? data.data : [];
    } catch (error) {
      console.error('Error fetching news:', error);
      return this.getMockNews(); // Fallback to mock data
    }
  }

  // Get user blogs (mock for now)
  async getUserBlogs(userId: string): Promise<BlogPost[]> {
    // This would connect to your backend
    return this.getMockBlogs();
  }

  // Create new blog post
  async createBlogPost(blogData: Partial<BlogPost>): Promise<BlogPost> {
    // Mock implementation - replace with actual API call
    const newBlog: BlogPost = {
      id: Date.now().toString(),
      title: blogData.title || '',
      content: blogData.content || '',
      excerpt: blogData.excerpt || '',
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
    
    return newBlog;
  }

  // Mock data fallback
  private getMockNews(): NewsArticle[] {
    return [
      {
        id: '1',
        title: 'Haaland Fit for Manchester Derby',
        content: 'Erling Haaland has been declared fit for the upcoming Manchester derby...',
        excerpt: 'Manchester City receive major boost as star striker returns to training',
        author: 'Premier League News',
        publishedAt: new Date().toISOString(),
        source: 'BBC Sport',
        category: 'injury',
        type: 'news',
        likes: 142,
        comments: 23
      },
      {
        id: '2',
        title: 'Arsenal Close in on January Signing',
        content: 'Arsenal are reportedly close to completing a deal for...',
        excerpt: 'Gunners set to strengthen squad in January transfer window',
        author: 'Transfer News',
        publishedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        source: 'Sky Sports',
        category: 'transfer',
        type: 'news',
        likes: 89,
        comments: 45
      }
    ];
  }

  private getMockBlogs(): BlogPost[] {
    return [
      {
        id: 'blog1',
        title: 'My Analysis: Title Race Predictions',
        content: 'After careful analysis of the current form...',
        excerpt: 'Breaking down the Premier League title race with data insights',
        author: {
          id: 'user1',
          name: 'Football Analyst',
          avatar: '/avatars/analyst.jpg'
        },
        publishedAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        tags: ['analysis', 'predictions', 'title-race'],
        likes: 15,
        comments: 3,
        isPublished: true
      }
    ];
  }
}

export const newsService = new NewsService();