export interface NewsArticle {
  id: string;
  title: string;
  content: string;
  excerpt: string;
  author: string;
  publishedAt: string;
  source: string;
  link?: string;
  imageUrl?: string;
  category: 'transfer' | 'injury' | 'match' | 'general' | 'analysis';
  type: 'news' | 'user_blog';
  likes: number;
  comments: number;
  isUserLiked?: boolean;
}

export interface BlogPost {
  id: string;
  title: string;
  content: string;
  excerpt: string;
  author: {
    id: string;
    name: string;
    avatar?: string;
  };
  publishedAt: string;
  tags: string[];
  likes: number;
  comments: number;
  isPublished: boolean;
}

export interface NewsState {
  articles: NewsArticle[];
  userBlogs: BlogPost[];
  featuredArticle: NewsArticle | null;
  loading: boolean;
  filters: {
    category: string;
    type: string;
    sortBy: string;
  };
  savedArticles: string[]; // Add this line
}