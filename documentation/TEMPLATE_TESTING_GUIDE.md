# 🧪 Template System Testing Guide

## Quick Test Checklist

### 1. Navigate to Create New Tab
- Click "Create New" in the navigation
- You should see the split button: `[New Container][▼]`

### 2. Test Dropdown Menu
- Click the dropdown arrow (▼)
- Dropdown should appear with 4 categories:
  - 🖥️ Development Container
  - ⛏️ Minecraft Server
  - 🎮 Game Server
  - 📦 Custom Container
- Click outside to close dropdown
- Click dropdown again to reopen

### 3. Test Category Selection
**Try Development Container:**
- Click "🖥️ Development Container"
- Should see template cards: Node.js, Python, PHP, Nginx
- Each card should have an icon and description

### 4. Test Template Selection
**Try Node.js:**
- Click the Node.js card
- Form should appear with:
  - Container Name field
  - Docker Image (pre-filled: `node`)
  - Version dropdown (20-alpine, 18-alpine, etc.)
  - Subdomain field
  - Internal Port (pre-filled: 3000)
  - Environment Variables section with checkboxes:
    - NODE_ENV (dropdown)
    - PORT (number)
    - DATABASE_URL (text, optional)
    - API_KEY (text, optional)
  - Resource Limits section

### 5. Test Environment Variable Checkboxes
- Uncheck NODE_ENV → input should disable
- Check NODE_ENV → input should enable
- Try changing values in enabled inputs

### 6. Test Form Submission
**Create a test container:**
```
Name: test-node-app
Image: node (pre-filled)
Tag: 20-alpine
Subdomain: testnode
Port: 3000
Environment:
  ☑ NODE_ENV: production
  ☑ PORT: 3000
  ☐ DATABASE_URL: (leave unchecked)
CPU: 1.0
Memory: 512
```
- Click "Create Container"
- Should see "Creating container..." notification
- Should see success notification
- Should switch to Containers view
- Should see your new container listed

### 7. Test Back Button
- Go back to Create New
- Select a category and template
- Click "← Back to Selection"
- Should return to template cards
- Form should be hidden

### 8. Test Different Templates

**Minecraft Server (Vanilla):**
- Select Minecraft Server → Vanilla
- Should see:
  - EULA checkbox (required, checked, disabled)
  - Version dropdown
  - Difficulty dropdown
  - Game Mode dropdown
  - Max Players number input
  - PVP checkbox
  - Memory recommendation badge

**Game Server (Valheim):**
- Select Game Server → Valheim
- Should see:
  - Server Name (required)
  - World Name (required)
  - Server Password (required, password type)
  - Public Server checkbox

**Custom Container:**
- Select Custom Container
- Should see manual inputs for all fields
- No pre-filled values

## Expected Behavior

### ✅ Working Features
- Dropdown toggles on/off
- Category selection shows templates
- Template selection shows form
- Form fields are pre-filled correctly
- Environment variable checkboxes enable/disable inputs
- Required fields are marked with *
- Memory recommendations show for game servers
- Form submission creates container
- Back button returns to selection
- Form resets after submission

### 🐛 Common Issues to Check

**If dropdown doesn't appear:**
- Check browser console for errors
- Verify templates.js is loaded
- Check CSS for `.dropdown-menu.show`

**If template cards don't show:**
- Check console for "Category not found" error
- Verify CONTAINER_TEMPLATES is defined
- Check if category name matches

**If form doesn't generate:**
- Check console for template errors
- Verify getTemplate() function works
- Check if dynamic-form-fields div exists

**If env var checkboxes don't work:**
- Check if toggleEnvVarInput is defined
- Verify checkbox IDs match input IDs
- Check console for JavaScript errors

**If submission fails:**
- Check network tab for GraphQL errors
- Verify backend is running
- Check if all required fields are filled
- Verify environment object is built correctly

## Browser Console Commands

Test template system manually:

```javascript
// Check if templates are loaded
console.log(CONTAINER_TEMPLATES);

// Get a specific template
console.log(getTemplate('development', 'nodejs'));

// Check current selection
console.log({
    category: selectedCategory,
    type: selectedType,
    template: currentTemplate
});

// Test dropdown
toggleDropdown();

// Test category selection
selectCategory('development');

// Test template selection
selectTemplate('development', 'nodejs');
```

## Testing Each Template Type

### Development Containers
- [ ] Node.js - Port 3000, NODE_ENV dropdown
- [ ] Python - Port 8000, PYTHONUNBUFFERED checkbox
- [ ] PHP - Port 80, PHP_MEMORY_LIMIT
- [ ] Nginx - Port 80, minimal config

### Minecraft Servers
- [ ] Vanilla - EULA required, version selection
- [ ] Paper - TYPE hidden field, version selection
- [ ] Spigot - TYPE hidden field, version selection

### Game Servers
- [ ] Valheim - Server name, world, password required
- [ ] Terraria - World name, optional password

### Custom
- [ ] Custom - All manual inputs, no pre-fills

## Success Criteria

✅ **MVP Complete** when:
1. Dropdown works
2. All categories show templates
3. All templates generate forms
4. Forms submit successfully
5. Containers are created in database
6. No console errors

✅ **Full Feature Complete** when:
1. All MVP criteria met
2. All 10 templates tested
3. Environment variables work correctly
4. Validation prevents errors
5. UI is responsive
6. Notifications work
7. Navigation flows smoothly

## Performance Checks

- Page load time: < 2 seconds
- Dropdown animation: smooth
- Form generation: instant
- Template switching: < 500ms
- Form submission: < 3 seconds

## Accessibility Checks

- [ ] Keyboard navigation works
- [ ] Tab order is logical
- [ ] Required fields are marked
- [ ] Error messages are clear
- [ ] Labels are associated with inputs

---

**Happy Testing!** 🎉

If you find any bugs, check the browser console first, then review the JavaScript in app.js.
