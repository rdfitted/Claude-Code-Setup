# Performance Testing Checklist

## Core Web Vitals
- [ ] First Contentful Paint (FCP) < 1.8s
- [ ] Largest Contentful Paint (LCP) < 2.5s
- [ ] First Input Delay (FID) < 100ms
- [ ] Cumulative Layout Shift (CLS) < 0.1
- [ ] Time to Interactive (TTI) < 3.8s
- [ ] Total Blocking Time (TBT) < 200ms

## Page Load Performance
- [ ] Initial page load completes quickly
- [ ] Page is usable before fully loaded
- [ ] Above-the-fold content loads first
- [ ] Deferred resources don't block rendering
- [ ] Critical CSS is inlined
- [ ] JavaScript doesn't block page render

## Resource Optimization
- [ ] Images are optimized and compressed
- [ ] Images use appropriate formats (WebP, AVIF)
- [ ] Images have proper dimensions (not scaled via CSS)
- [ ] Lazy loading implemented for below-fold images
- [ ] JavaScript bundles are minified
- [ ] CSS is minified and optimized
- [ ] Unused code is removed (tree-shaking)
- [ ] Code splitting reduces initial bundle size

## Network Performance
- [ ] Assets are served via CDN
- [ ] Compression enabled (Gzip/Brotli)
- [ ] Caching headers properly configured
- [ ] HTTP/2 or HTTP/3 is used
- [ ] DNS prefetch for external domains
- [ ] Preconnect for critical third-party origins
- [ ] Resource hints optimize loading order

## Runtime Performance
- [ ] No layout thrashing during interactions
- [ ] Smooth 60fps scrolling
- [ ] Animations use GPU acceleration (transform, opacity)
- [ ] No memory leaks during extended use
- [ ] Event handlers don't block main thread
- [ ] Virtual scrolling for long lists
- [ ] Debouncing/throttling on frequent events

## API & Data Loading
- [ ] API response times are acceptable (< 500ms)
- [ ] Parallel requests don't overwhelm server
- [ ] Data is paginated for large datasets
- [ ] Caching reduces redundant requests
- [ ] Stale-while-revalidate strategy used where appropriate
- [ ] Loading states prevent user confusion
- [ ] Failed requests retry with exponential backoff

## Mobile Performance
- [ ] App performs well on 3G/4G connections
- [ ] App performs well on older mobile devices
- [ ] Touch interactions are responsive
- [ ] Battery usage is reasonable
- [ ] Data usage is optimized

## Rendering Performance
- [ ] Minimal reflows and repaints
- [ ] No forced synchronous layouts
- [ ] Composite layers used appropriately
- [ ] Paint areas are minimal during interactions
- [ ] No unnecessary re-renders in React/Vue/Angular

## Third-Party Performance
- [ ] Third-party scripts load asynchronously
- [ ] Third-party scripts don't block rendering
- [ ] Analytics load after page is interactive
- [ ] Ads don't degrade core experience
- [ ] Social widgets load on-demand

## Bundle Analysis
- [ ] Main bundle size < 200KB (gzipped)
- [ ] Total JavaScript < 500KB (gzipped)
- [ ] No duplicate dependencies
- [ ] Tree-shaking eliminates dead code
- [ ] Code splitting by route implemented
- [ ] Vendor bundles separated and cached

## Database & Backend
- [ ] Database queries are optimized
- [ ] Indexes exist for frequently queried fields
- [ ] N+1 queries are eliminated
- [ ] Caching layer reduces database load
- [ ] CDN caches static assets
- [ ] Server response time < 200ms (TTFB)

## Performance Budget
- [ ] Page weight stays within budget
- [ ] JavaScript execution time within budget
- [ ] Number of requests within budget
- [ ] Performance metrics monitored continuously
- [ ] Performance regression alerts configured

## Stress Testing
- [ ] App handles 100+ concurrent users
- [ ] App handles 1000+ concurrent users (if applicable)
- [ ] App gracefully degrades under high load
- [ ] Rate limiting prevents abuse
- [ ] Queue system handles traffic spikes
