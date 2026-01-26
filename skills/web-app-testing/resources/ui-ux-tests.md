# UI/UX Testing Checklist

## Visual Design
- [ ] Color scheme is consistent throughout
- [ ] Typography is consistent and readable
- [ ] Spacing and alignment are uniform
- [ ] Brand guidelines are followed
- [ ] Icons and images are high quality
- [ ] Loading spinners/skeletons appear appropriately

## Responsive Design
- [ ] Layout adapts to desktop (1920x1080)
- [ ] Layout adapts to tablet (768x1024)
- [ ] Layout adapts to mobile (375x667)
- [ ] Touch targets are large enough (min 44x44px)
- [ ] No horizontal scrolling on mobile
- [ ] Text is readable without zooming
- [ ] Images scale appropriately

## Accessibility (WCAG 2.1 AA)
- [ ] All images have alt text
- [ ] Color contrast meets 4.5:1 ratio for text
- [ ] Keyboard navigation works for all interactive elements
- [ ] Focus indicators are visible
- [ ] Form labels are properly associated
- [ ] Error messages are announced to screen readers
- [ ] Headings follow proper hierarchy (h1, h2, h3...)
- [ ] ARIA labels present where needed

## Interactive Elements
- [ ] Buttons have hover states
- [ ] Buttons have active/pressed states
- [ ] Buttons have disabled states when appropriate
- [ ] Links are visually distinguishable
- [ ] Form inputs have focus states
- [ ] Clickable elements have cursor pointer
- [ ] Transitions and animations are smooth

## User Feedback
- [ ] Loading states prevent confusion during waits
- [ ] Success states provide positive reinforcement
- [ ] Error states clearly indicate issues
- [ ] Progress indicators show completion status
- [ ] Confirmation messages prevent accidental actions
- [ ] Tooltips provide helpful context

## Navigation & Information Architecture
- [ ] Primary navigation is easy to find
- [ ] Current page is highlighted in navigation
- [ ] Breadcrumbs show user location
- [ ] Search is easily accessible
- [ ] Important actions are prominently displayed
- [ ] Related content is grouped logically

## Forms & Input UX
- [ ] Input fields have clear labels
- [ ] Placeholder text provides helpful examples
- [ ] Required fields are clearly marked
- [ ] Error messages are specific and helpful
- [ ] Multi-step forms show progress
- [ ] Auto-save prevents data loss
- [ ] Password visibility toggle available

## Content & Readability
- [ ] Text uses appropriate font sizes (min 16px body)
- [ ] Line length is comfortable (50-75 characters)
- [ ] Line height provides adequate spacing
- [ ] Content hierarchy is clear
- [ ] Important information is emphasized
- [ ] Long content is broken into sections

## Performance Perception
- [ ] Initial page load feels fast
- [ ] Interactions feel responsive
- [ ] Skeleton screens reduce perceived wait time
- [ ] Optimistic UI updates improve perceived speed
- [ ] No janky animations or reflows

## Mobile-Specific UX
- [ ] Touch gestures work intuitively (swipe, pinch)
- [ ] No hover-dependent interactions
- [ ] Keyboard doesn't obscure important content
- [ ] Scrolling is smooth without lag
- [ ] Modal dialogs are easy to dismiss

## Cross-Browser Consistency
- [ ] Layout consistent in Chrome
- [ ] Layout consistent in Firefox
- [ ] Layout consistent in Safari
- [ ] Layout consistent in Edge
- [ ] Features degrade gracefully in older browsers

## Dark Mode (if applicable)
- [ ] Dark mode toggle is accessible
- [ ] All colors adapt appropriately
- [ ] Contrast remains sufficient in dark mode
- [ ] Images/logos adapt or have dark versions
- [ ] User preference is remembered
