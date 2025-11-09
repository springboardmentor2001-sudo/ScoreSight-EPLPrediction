import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Avatar
} from '@mui/material';
import { Favorite, FavoriteBorder, Comment } from '@mui/icons-material';
import { NewsArticle } from '../../types/news';

interface NewsCardProps {
  article: NewsArticle;
  onLike: (id: string) => void;
  featured?: boolean;
}

const NewsCard: React.FC<NewsCardProps> = ({ article, onLike, featured = false }) => {
  const categoryColors = {
    transfer: 'primary',
    injury: 'error',
    match: 'success',
    general: 'default',
    analysis: 'warning'
  } as const;

  return (
    <Card 
      sx={{ 
        height: '100%',
        transition: 'all 0.3s ease',
        border: featured ? '2px solid #1976d2' : '1px solid #e0e0e0',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
        }
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Chip 
            label={article.category.toUpperCase()} 
            size="small"
            color={categoryColors[article.category]}
          />
          <Typography variant="caption" color="text.secondary">
            {new Date(article.publishedAt).toLocaleDateString()}
          </Typography>
        </Box>

        <Typography 
          variant={featured ? "h5" : "h6"} 
          component="h2" 
          gutterBottom
          sx={{ 
            fontWeight: 600,
            lineHeight: 1.3
          }}
        >
          {article.title}
        </Typography>

        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ mb: 2 }}
        >
          {article.excerpt}
        </Typography>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Avatar sx={{ width: 24, height: 24 }}>
              {article.source.charAt(0)}
            </Avatar>
            <Typography variant="caption">
              {article.source}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton 
              size="small" 
              onClick={() => onLike(article.id)}
              color={article.isUserLiked ? 'error' : 'default'}
            >
              {article.isUserLiked ? <Favorite /> : <FavoriteBorder />}
            </IconButton>
            <Typography variant="caption">{article.likes}</Typography>
            
            <Comment sx={{ fontSize: 16, ml: 1, color: 'text.secondary' }} />
            <Typography variant="caption">{article.comments}</Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default NewsCard;