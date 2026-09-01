# Code Standards

- **HTML:** semantic sections, accessible labels, proper headings.
- **CSS:** mobile-first, BEM or utility classes, CSS variables for themes.
- **JavaScript:** small pure functions; avoid global state; modules where possible.
- **Docs:** each feature ships with a short “how it works” note.

## JSDoc example
```js
/**
 * Calculate weighted average percentage.
 * @param {Array<{earned:number, possible:number, weight:number}>} items
 * @returns {number} Percentage in [0,100].
 */
```
