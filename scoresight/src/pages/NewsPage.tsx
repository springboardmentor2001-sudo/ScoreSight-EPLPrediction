import React, { useEffect, useState } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Avatar,
  Chip,
  Paper,
  Skeleton,
  IconButton,
  Fade,
  InputAdornment,
  ToggleButton,
  ToggleButtonGroup,
  Tabs,
  Tab
} from '@mui/material';
import {
  Add,
  Search,
  Whatshot,
  NewReleases,
  Favorite,
  FavoriteBorder,
  Comment,
  Bookmark,
  BookmarkBorder,
  Article
} from '@mui/icons-material';
import { useNews } from '../contexts/NewsContext';
import { NewsArticle } from '../types/news';
import BlogEditor from '../components/news/BlogEditor';

const NewsPage: React.FC = () => {
  const {
    articles,
    userBlogs,
    featuredArticle,
    loading,
    filters,
    savedArticles,
    fetchNews,
    createBlog,
    likeArticle,
    toggleSavedArticle,
    setFilters
  } = useNews();

  const [editorOpen, setEditorOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState(0); // 0 = News, 1 = Saved Articles, 2 = My Blogs

  useEffect(() => {
    fetchNews();
  }, []);

  const handleCreateBlog = async (blogData: { title: string; content: string; tags: string[] }) => {
    try {
      await createBlog(blogData);
      alert('Blog published successfully!');
    } catch (error) {
      console.error('Failed to create blog:', error);
      alert('Failed to publish blog. Please try again.');
    }
  };

  const handleFilterChange = (event: React.MouseEvent<HTMLElement>, newValue: string) => {
    setFilters({ category: newValue });
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Filter articles based on search and category
  const filteredArticles = articles.filter(article => {
    const matchesSearch = article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                       article.excerpt.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory = filters.category === 'all' || article.category === filters.category;
    
    return matchesSearch && matchesCategory;
  });

  // Get saved articles
  const savedArticlesList = articles.filter(article => 
    savedArticles.includes(article.id)
  );

  const NewsCardComponent: React.FC<{ article: NewsArticle; featured?: boolean }> = ({ article, featured = false }) => {
    const categoryColors = {
      transfer: 'primary',
      injury: 'error',
      match: 'success',
      general: 'default',
      analysis: 'warning'
    } as const;

    // Safe category handling
    const category = article.category || 'general';
    const safeCategory = categoryColors[category] ? category : 'general';

    const isSaved = savedArticles.includes(article.id);

    const handleArticleClick = () => {
      if (article.link) {
        window.open(article.link, '_blank', 'noopener,noreferrer');
      } else {
        // Fallback: show alert with title
        alert(`Opening: ${article.title}\n\nThis would open the full article in a new tab.`);
      }
    };

    return (
      <Card 
        sx={{ 
          height: '100%',
          transition: 'all 0.3s ease',
          border: featured ? '2px solid #1976d2' : '1px solid rgba(0, 212, 255, 0.1)',
          background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)',
          cursor: 'pointer',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
            borderColor: '#00d4ff'
          }
        }}
        onClick={handleArticleClick}
      >
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Chip 
              label={(safeCategory || 'general').toUpperCase()} 
              size="small"
              color={categoryColors[safeCategory]}
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
              lineHeight: 1.3,
              color: '#ffffff'
            }}
          >
            {article.title || 'Untitled Article'}
          </Typography>

          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ mb: 2, lineHeight: 1.6 }}
          >
            {article.excerpt || 'No description available.'}
          </Typography>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Avatar sx={{ width: 24, height: 24, bgcolor: 'primary.main' }}>
                {(article.source || 'N').charAt(0)}
              </Avatar>
              <Typography variant="caption" color="text.secondary">
                {article.source || 'Unknown Source'}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <IconButton 
                size="small" 
                onClick={(e) => {
                  e.stopPropagation();
                  toggleSavedArticle(article.id);
                }}
                color={isSaved ? 'primary' : 'default'}
              >
                {isSaved ? <Bookmark /> : <BookmarkBorder />}
              </IconButton>

              <IconButton 
                size="small" 
                onClick={(e) => {
                  e.stopPropagation();
                  likeArticle(article.id);
                }}
                color={article.isUserLiked ? 'error' : 'default'}
              >
                {article.isUserLiked ? <Favorite /> : <FavoriteBorder />}
              </IconButton>
              <Typography variant="caption" color="text.secondary">{article.likes || 0}</Typography>
              
              <Comment sx={{ fontSize: 16, ml: 1, color: 'text.secondary' }} />
              <Typography variant="caption" color="text.secondary">{article.comments || 0}</Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  };

  // Render content based on active tab
  const renderContent = () => {
    switch (activeTab) {
      case 0: // News Tab
        return (
          <>
            {/* Featured Story */}
            {featuredArticle && !loading && (
              <Box sx={{ mb: 4 }}>
                <Typography variant="h5" gutterBottom sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  color: '#00d4ff',
                  fontWeight: 600
                }}>
                  <Whatshot sx={{ mr: 1, color: 'orange' }} />
                  FEATURED STORY
                </Typography>
                <NewsCardComponent 
                  article={featuredArticle} 
                  featured
                />
              </Box>
            )}

            {/* Latest News */}
            <Typography variant="h5" gutterBottom sx={{ 
              mb: 3,
              display: 'flex', 
              alignItems: 'center',
              color: '#ff6bff',
              fontWeight: 600
            }}>
              <NewReleases sx={{ mr: 1 }} />
              LATEST NEWS
            </Typography>

            {loading ? (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {[1, 2, 3, 4, 5, 6].map(i => (
                  <Card key={i}>
                    <CardContent>
                      <Skeleton variant="text" height={40} />
                      <Skeleton variant="text" height={20} />
                      <Skeleton variant="rectangular" height={100} sx={{ mt: 2, borderRadius: 2 }} />
                    </CardContent>
                  </Card>
                ))}
              </Box>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {filteredArticles.slice(0, 6).map(article => (
                  <NewsCardComponent key={article.id} article={article} />
                ))}
              </Box>
            )}
          </>
        );

      case 1: // Saved Articles Tab
        return (
          <>
            <Typography variant="h5" gutterBottom sx={{ 
              mb: 3,
              display: 'flex', 
              alignItems: 'center',
              color: '#00d4ff',
              fontWeight: 600
            }}>
              <Bookmark sx={{ mr: 1 }} />
              SAVED ARTICLES ({savedArticlesList.length})
            </Typography>

            {savedArticlesList.length === 0 ? (
              <Card sx={{ textAlign: 'center', p: 4 }}>
                <CardContent>
                  <BookmarkBorder sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No Saved Articles
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Save articles by clicking the bookmark icon on any news card.
                  </Typography>
                </CardContent>
              </Card>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {savedArticlesList.map(article => (
                  <NewsCardComponent key={article.id} article={article} />
                ))}
              </Box>
            )}
          </>
        );

      case 2: // My Blogs Tab
        return (
          <>
            <Typography variant="h5" gutterBottom sx={{ 
              mb: 3,
              display: 'flex', 
              alignItems: 'center',
              color: '#ff6bff',
              fontWeight: 600
            }}>
              <Article sx={{ mr: 1 }} />
              MY BLOGS ({userBlogs.length})
            </Typography>

            {userBlogs.length === 0 ? (
              <Card sx={{ textAlign: 'center', p: 4 }}>
                <CardContent>
                  <Article sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No Blogs Yet
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Start writing your first blog post!
                  </Typography>
                  <Button 
                    variant="contained" 
                    startIcon={<Add />}
                    onClick={() => setEditorOpen(true)}
                    sx={{ 
                      background: 'linear-gradient(45deg, #00d4ff, #ff6bff)',
                      fontWeight: 600
                    }}
                  >
                    Write Your First Blog
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {userBlogs.map(blog => (
                  <Paper 
                    key={blog.id} 
                    sx={{ 
                      p: 3, 
                      background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(255, 107, 255, 0.05) 100%)',
                      border: '1px solid rgba(0, 212, 255, 0.2)',
                      borderRadius: 2,
                      cursor: 'pointer',
                      '&:hover': {
                        borderColor: '#00d4ff',
                        transform: 'translateY(-2px)',
                        transition: 'all 0.3s ease'
                      }
                    }}
                  >
                    <Typography variant="h6" fontWeight="600" gutterBottom sx={{ color: '#ffffff' }}>
                      {blog.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2, lineHeight: 1.6 }}>
                      {blog.excerpt}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {blog.tags.map(tag => (
                          <Chip 
                            key={tag} 
                            label={tag} 
                            size="small" 
                            sx={{ 
                              backgroundColor: 'rgba(255, 107, 255, 0.1)',
                              color: '#ff6bff',
                              border: '1px solid rgba(255, 107, 255, 0.3)'
                            }}
                          />
                        ))}
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(blog.publishedAt).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </Paper>
                ))}
              </Box>
            )}
          </>
        );

      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" component="h1" gutterBottom 
          sx={{ 
            background: 'linear-gradient(45deg, #00d4ff, #ff6bff)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            color: 'transparent',
            fontWeight: 700
          }}>
          NEWS & BLOGS HUB
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
          Latest Premier League updates and community insights
        </Typography>
      </Box>

      {/* Tabs */}
      <Card sx={{ mb: 4, background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)' }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{
            '& .MuiTab-root': {
              color: 'text.secondary',
              fontWeight: 600,
              fontSize: '0.9rem'
            },
            '& .Mui-selected': {
              color: '#00d4ff',
            },
            '& .MuiTabs-indicator': {
              backgroundColor: '#00d4ff',
            }
          }}
        >
          <Tab icon={<NewReleases />} label="LATEST NEWS" />
          <Tab icon={<Bookmark />} label="SAVED ARTICLES" />
          <Tab icon={<Article />} label="MY BLOGS" />
        </Tabs>
      </Card>

      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 4 }}>
        {/* Main Content Section */}
        <Box sx={{ flex: 2 }}>
          {/* Search and Filters - Only show on News tab */}
          {activeTab === 0 && (
            <Fade in={true} timeout={800}>
              <Card sx={{ 
                background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)',
                border: '1px solid rgba(0, 212, 255, 0.1)',
                borderRadius: 3,
                p: 2,
                mb: 3
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
                    <TextField
                      placeholder="Search news and blogs..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Search />
                          </InputAdornment>
                        ),
                      }}
                      sx={{ 
                        minWidth: 250,
                        '& .MuiOutlinedInput-root': {
                          '&:hover fieldset': {
                            borderColor: '#00d4ff',
                          },
                        }
                      }}
                    />
                    
                    <ToggleButtonGroup
                      value={filters.category}
                      exclusive
                      onChange={handleFilterChange}
                    >
                      <ToggleButton value="all">All</ToggleButton>
                      <ToggleButton value="transfer">Transfers</ToggleButton>
                      <ToggleButton value="injury">Injuries</ToggleButton>
                      <ToggleButton value="match">Matches</ToggleButton>
                      <ToggleButton value="analysis">Analysis</ToggleButton>
                    </ToggleButtonGroup>

                    <Button
                      variant="contained"
                      startIcon={<Add />}
                      onClick={() => setEditorOpen(true)}
                      sx={{ 
                        ml: 'auto',
                        background: 'linear-gradient(45deg, #00d4ff, #ff6bff)',
                        fontWeight: 600
                      }}
                    >
                      Write Blog
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Fade>
          )}

          {/* Render content based on active tab */}
          {renderContent()}
        </Box>

        {/* Sidebar Section - Only show on News tab */}
        {activeTab === 0 && (
          <Box sx={{ flex: 1 }}>
            {/* Quick Actions */}
            <Fade in={true} timeout={1000}>
              <Card sx={{ 
                background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)',
                border: '1px solid rgba(255, 107, 255, 0.1)',
                borderRadius: 3,
                p: 2,
                mb: 3
              }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ 
                    color: '#ff6bff',
                    fontWeight: 600
                  }}>
                    QUICK ACTIONS
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Button 
                      variant="outlined" 
                      startIcon={<Add />}
                      onClick={() => setEditorOpen(true)}
                      sx={{ 
                        borderColor: '#00d4ff',
                        color: '#00d4ff',
                        '&:hover': {
                          borderColor: '#00a8cc',
                          backgroundColor: 'rgba(0, 212, 255, 0.1)'
                        }
                      }}
                    >
                      Write New Blog
                    </Button>
                    <Button 
                      variant="outlined" 
                      startIcon={<Bookmark />}
                      onClick={() => setActiveTab(1)}
                      sx={{ borderColor: '#ff6bff', color: '#ff6bff' }}
                    >
                      View Saved Articles
                    </Button>
                    <Button 
                      variant="outlined" 
                      startIcon={<Article />}
                      onClick={() => setActiveTab(2)}
                      sx={{ borderColor: '#00ff88', color: '#00ff88' }}
                    >
                      My Blogs
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Fade>

            {/* Popular Tags */}
            <Fade in={true} timeout={1400}>
              <Card sx={{ 
                background: 'linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%)',
                border: '1px solid rgba(255, 107, 255, 0.1)',
                borderRadius: 3,
                p: 2
              }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ 
                    color: '#ff6bff',
                    fontWeight: 600
                  }}>
                    POPULAR TAGS
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {['TransferNews', 'InjuryUpdate', 'MatchAnalysis', 'Tactics', 'TitleRace', 'Relegation'].map(tag => (
                      <Chip 
                        key={tag} 
                        label={`#${tag}`} 
                        variant="outlined"
                        clickable
                        sx={{
                          borderColor: '#ff6bff',
                          color: '#ff6bff',
                          '&:hover': {
                            backgroundColor: 'rgba(255, 107, 255, 0.1)'
                          }
                        }}
                      />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Fade>
          </Box>
        )}
      </Box>

      {/* Blog Editor */}
      <BlogEditor
        open={editorOpen}
        onClose={() => setEditorOpen(false)}
        onSubmit={handleCreateBlog}
      />
    </Box>
  );
};

export default NewsPage;