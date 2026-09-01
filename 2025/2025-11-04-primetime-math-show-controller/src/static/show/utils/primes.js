/**
 * Prime number utilities
 * Used by Ulam Spiral and other math visual presets
 */

/**
 * Check if a number is prime
 * @param {number} n - Number to check
 * @returns {boolean} True if prime
 */
export function isPrime(n) {
    if (n < 2) return false;
    if (n === 2) return true;
    if (n % 2 === 0) return false;
    
    const sqrt = Math.sqrt(n);
    for (let i = 3; i <= sqrt; i += 2) {
        if (n % i === 0) return false;
    }
    return true;
}

/**
 * Generate array of primes up to a limit
 * @param {number} limit - Maximum prime value
 * @returns {Array<number>} Array of primes
 */
export function generatePrimes(limit) {
    const primes = [];
    for (let i = 2; i <= limit; i++) {
        if (isPrime(i)) {
            primes.push(i);
        }
    }
    return primes;
}

/**
 * Get first N primes
 * @param {number} count - Number of primes to generate
 * @returns {Array<number>} Array of primes
 */
export function getFirstNPrimes(count) {
    const primes = [];
    let num = 2;
    while (primes.length < count) {
        if (isPrime(num)) {
            primes.push(num);
        }
        num++;
    }
    return primes;
}

