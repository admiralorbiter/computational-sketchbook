//! matching: extensible matching strategies for room discovery
//!
//! This crate provides a foundation for different matching strategies that can be
//! swapped out as the system scales. Currently, keyword matching is implemented
//! in the web handler, but future strategies (embeddings, collaborative filtering,
//! etc.) can be implemented here.

use async_trait::async_trait;
use serde::{Deserialize, Serialize};

/// Metadata about a room used for matching
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RoomMetadata {
    pub id: String,
    pub title: String,
    pub tags: String,
    pub description: String,
    pub activity_score: f64,
    pub member_count: i32,
    pub language: String,
}

/// Trait for matching strategies
///
/// Different strategies can be implemented:
/// - KeywordMatcher (current MVP implementation)
/// - EmbeddingMatcher (future: semantic similarity)
/// - CollaborativeMatcher (future: privacy-preserving collaborative filtering)
/// - ContextualMatcher (future: time-based, trending topics)
#[async_trait]
pub trait MatchingStrategy {
    /// Score a room based on user intent
    ///
    /// Returns a score between 0.0 and 1.0, where:
    /// - 1.0 = perfect match
    /// - 0.0 = no match
    async fn score(&self, intent: &str, room: &RoomMetadata) -> f64;
    
    /// Get the name/identifier of this strategy
    fn name(&self) -> &'static str;
}

// MVP: Keyword matching is currently implemented in apps/web/src/handlers/matching.rs
// Future implementations will be added here as separate structs implementing MatchingStrategy

// Example future implementation (commented out):
// 
// pub struct EmbeddingMatcher {
//     // Will use sentence-transformers or similar
//     // Computed on-device in browser, or via edge function
// }
// 
// #[async_trait]
// impl MatchingStrategy for EmbeddingMatcher {
//     async fn score(&self, intent: &str, room: &RoomMetadata) -> f64 {
//         // Implementation using embeddings
//         todo!()
//     }
//     
//     fn name(&self) -> &'static str {
//         "embedding_v1"
//     }
// }
