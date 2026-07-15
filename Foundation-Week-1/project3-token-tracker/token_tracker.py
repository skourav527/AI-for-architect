"""
Project 3: Token Usage Tracker
================================

GOAL: Build a system to monitor and optimize API token consumption

LEARNING OBJECTIVES:
- Data persistence (SQLite)
- Dataclasses and Pydantic models
- Aggregation and analysis
- Background tasks
- Rich tables for data visualization

TIME: 4-6 hours
REQUIRES: Project 1 and Project 2 completed
"""

import os
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import json
from contextlib import contextmanager
from pydantic import BaseModel, Field
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv

load_dotenv()
console = Console()


# =============================================================================
# DATA MODELS
# =============================================================================

class TokenUsage(BaseModel):
    """Model for a single API call's token usage"""
    id: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    provider: str = Field(..., description="openai, anthropic, etc.")
    model: str = Field(..., description="gpt-3.5-turbo, claude-3, etc.")
    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)
    cost_usd: float = Field(..., ge=0.0)
    user_id: Optional[str] = Field(default="default")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


@dataclass
class UsageStats:
    """Aggregated usage statistics"""
    total_requests: int
    total_tokens: int
    total_cost: float
    prompt_tokens: int
    completion_tokens: int
    avg_tokens_per_request: float
    providers: Dict[str, int]  # provider -> request count
    models: Dict[str, int]  # model -> request count


# =============================================================================
# PRICING DATA (as of 2024)
# =============================================================================

PRICING = {
    "openai": {
        "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},  # per 1K tokens
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
    },
    "anthropic": {
        "claude-3-5-sonnet-20241022": {"prompt": 0.003, "completion": 0.015},
        "claude-3-opus": {"prompt": 0.015, "completion": 0.075},
        "claude-3-sonnet": {"prompt": 0.003, "completion": 0.015},
    }
}


def calculate_cost(provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """
    Calculate cost in USD for an API call.
    
    Args:
        provider: Provider name (openai, anthropic)
        model: Model name
        prompt_tokens: Input tokens
        completion_tokens: Output tokens
        
    Returns:
        Cost in USD
    """
    provider_pricing = PRICING.get(provider.lower(), {})
    model_pricing = provider_pricing.get(model, {"prompt": 0.001, "completion": 0.002})
    
    prompt_cost = (prompt_tokens / 1000) * model_pricing["prompt"]
    completion_cost = (completion_tokens / 1000) * model_pricing["completion"]
    
    return prompt_cost + completion_cost


# =============================================================================
# DATABASE MANAGER
# =============================================================================

class TokenTrackerDB:
    """
    SQLite database for token usage tracking.
    
    This demonstrates:
    - Context managers for database connections
    - SQL operations (INSERT, SELECT, aggregations)
    - Data persistence
    """
    
    def __init__(self, db_path: str = "token_usage.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create database schema if it doesn't exist"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS token_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    cost_usd REAL NOT NULL,
                    user_id TEXT,
                    metadata TEXT
                )
            """)
            
            # Create indexes for common queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON token_usage(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_provider 
                ON token_usage(provider)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user 
                ON token_usage(user_id)
            """)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        try:
            yield conn
        finally:
            conn.close()
    
    def log_usage(self, usage: TokenUsage) -> int:
        """
        Log a token usage record.
        
        Args:
            usage: TokenUsage instance
            
        Returns:
            Record ID
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO token_usage 
                (timestamp, provider, model, prompt_tokens, completion_tokens, 
                 total_tokens, cost_usd, user_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                usage.timestamp.isoformat(),
                usage.provider,
                usage.model,
                usage.prompt_tokens,
                usage.completion_tokens,
                usage.total_tokens,
                usage.cost_usd,
                usage.user_id,
                json.dumps(usage.metadata) if usage.metadata else None
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_usage_history(
        self,
        limit: int = 100,
        provider: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[TokenUsage]:
        """
        Get usage history with optional filters.
        
        Args:
            limit: Maximum records to return
            provider: Filter by provider
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            List of TokenUsage records
        """
        query = "SELECT * FROM token_usage WHERE 1=1"
        params = []
        
        if provider:
            query += " AND provider = ?"
            params.append(provider)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                TokenUsage(
                    id=row["id"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    provider=row["provider"],
                    model=row["model"],
                    prompt_tokens=row["prompt_tokens"],
                    completion_tokens=row["completion_tokens"],
                    total_tokens=row["total_tokens"],
                    cost_usd=row["cost_usd"],
                    user_id=row["user_id"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {}
                )
                for row in rows
            ]
    
    def get_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None
    ) -> UsageStats:
        """
        Get aggregated usage statistics.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            user_id: User ID filter
            
        Returns:
            UsageStats object
        """
        query = """
            SELECT 
                COUNT(*) as total_requests,
                SUM(total_tokens) as total_tokens,
                SUM(cost_usd) as total_cost,
                SUM(prompt_tokens) as prompt_tokens,
                SUM(completion_tokens) as completion_tokens,
                AVG(total_tokens) as avg_tokens,
                provider,
                model
            FROM token_usage
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        with self._get_connection() as conn:
            # Get overall stats
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            
            if row["total_requests"] is None:
                # No data
                return UsageStats(
                    total_requests=0,
                    total_tokens=0,
                    total_cost=0.0,
                    prompt_tokens=0,
                    completion_tokens=0,
                    avg_tokens_per_request=0.0,
                    providers={},
                    models={}
                )
            
            # Get provider breakdown
            provider_query = query + " GROUP BY provider"
            provider_cursor = conn.execute(provider_query, params)
            providers = {row["provider"]: row["total_requests"] for row in provider_cursor}
            
            # Get model breakdown
            model_query = query + " GROUP BY model"
            model_cursor = conn.execute(model_query, params)
            models = {row["model"]: row["total_requests"] for row in model_cursor}
            
            return UsageStats(
                total_requests=row["total_requests"],
                total_tokens=row["total_tokens"],
                total_cost=row["total_cost"],
                prompt_tokens=row["prompt_tokens"],
                completion_tokens=row["completion_tokens"],
                avg_tokens_per_request=row["avg_tokens"],
                providers=providers,
                models=models
            )
    
    def get_daily_usage(self, days: int = 7) -> Dict[str, float]:
        """
        Get daily usage for the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict of date -> cost
        """
        start_date = datetime.now() - timedelta(days=days)
        
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    SUM(cost_usd) as daily_cost
                FROM token_usage
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (start_date.isoformat(),))
            
            return {row["date"]: row["daily_cost"] for row in cursor.fetchall()}


# =============================================================================
# TOKEN TRACKER (Main Class)
# =============================================================================

class TokenTracker:
    """
    Main token tracking interface.
    
    Usage:
        tracker = TokenTracker()
        
        # Log usage
        tracker.log(provider="openai", model="gpt-3.5-turbo", 
                   prompt_tokens=100, completion_tokens=50)
        
        # Get stats
        stats = tracker.get_stats()
        print(f"Total cost: ${stats.total_cost:.4f}")
        
        # Display report
        tracker.display_report()
    """
    
    def __init__(self, db_path: str = "token_usage.db"):
        self.db = TokenTrackerDB(db_path)
    
    def log(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        user_id: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log token usage.
        
        Args:
            provider: Provider name
            model: Model name
            prompt_tokens: Input tokens
            completion_tokens: Output tokens
            user_id: User identifier
            metadata: Additional metadata
            
        Returns:
            Record ID
        """
        total_tokens = prompt_tokens + completion_tokens
        cost = calculate_cost(provider, model, prompt_tokens, completion_tokens)
        
        usage = TokenUsage(
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            user_id=user_id,
            metadata=metadata or {}
        )
        
        record_id = self.db.log_usage(usage)
        console.print(f"[dim]💰 Logged: {total_tokens} tokens, ${cost:.4f}[/dim]")
        return record_id
    
    def get_stats(self, days: Optional[int] = None) -> UsageStats:
        """
        Get usage statistics.
        
        Args:
            days: Number of days to look back (None for all time)
            
        Returns:
            UsageStats object
        """
        start_date = None
        if days:
            start_date = datetime.now() - timedelta(days=days)
        
        return self.db.get_stats(start_date=start_date)
    
    def display_report(self, days: Optional[int] = None):
        """
        Display a beautiful usage report.
        
        Args:
            days: Number of days to include (None for all time)
        """
        stats = self.get_stats(days)
        
        # Header
        period = f"Last {days} days" if days else "All time"
        console.print(Panel.fit(
            f"[bold cyan]Token Usage Report[/bold cyan]\n{period}",
            border_style="cyan"
        ))
        
        # Overall stats table
        overall_table = Table(title="Overall Statistics", show_header=False)
        overall_table.add_column("Metric", style="cyan")
        overall_table.add_column("Value", style="yellow")
        
        overall_table.add_row("Total Requests", f"{stats.total_requests:,}")
        overall_table.add_row("Total Tokens", f"{stats.total_tokens:,}")
        overall_table.add_row("Total Cost", f"${stats.total_cost:.4f}")
        overall_table.add_row("Avg Tokens/Request", f"{stats.avg_tokens_per_request:.1f}")
        overall_table.add_row("Prompt Tokens", f"{stats.prompt_tokens:,}")
        overall_table.add_row("Completion Tokens", f"{stats.completion_tokens:,}")
        
        console.print(overall_table)
        console.print()
        
        # Provider breakdown
        if stats.providers:
            provider_table = Table(title="By Provider")
            provider_table.add_column("Provider", style="cyan")
            provider_table.add_column("Requests", style="yellow", justify="right")
            
            for provider, count in sorted(stats.providers.items(), key=lambda x: x[1], reverse=True):
                provider_table.add_row(provider, f"{count:,}")
            
            console.print(provider_table)
            console.print()
        
        # Model breakdown
        if stats.models:
            model_table = Table(title="By Model")
            model_table.add_column("Model", style="cyan")
            model_table.add_column("Requests", style="yellow", justify="right")
            
            for model, count in sorted(stats.models.items(), key=lambda x: x[1], reverse=True):
                model_table.add_row(model, f"{count:,}")
            
            console.print(model_table)
    
    def display_recent(self, limit: int = 10):
        """Display recent usage records"""
        history = self.db.get_usage_history(limit=limit)
        
        table = Table(title=f"Recent {limit} Requests")
        table.add_column("Time", style="cyan")
        table.add_column("Provider", style="yellow")
        table.add_column("Model", style="yellow")
        table.add_column("Tokens", style="green", justify="right")
        table.add_column("Cost", style="red", justify="right")
        
        for record in history:
            table.add_row(
                record.timestamp.strftime("%Y-%m-%d %H:%M"),
                record.provider,
                record.model[:20],
                f"{record.total_tokens:,}",
                f"${record.cost_usd:.4f}"
            )
        
        console.print(table)
    
    def check_budget(self, budget_usd: float, days: int = 30):
        """
        Check if usage is within budget.
        
        Args:
            budget_usd: Monthly budget in USD
            days: Period to check
        """
        stats = self.get_stats(days=days)
        
        percentage = (stats.total_cost / budget_usd) * 100
        
        if percentage > 100:
            console.print(f"[red]⚠️  OVER BUDGET![/red] {percentage:.1f}% of ${budget_usd:.2f}")
        elif percentage > 80:
            console.print(f"[yellow]⚠️  Warning:[/yellow] {percentage:.1f}% of ${budget_usd:.2f}")
        else:
            console.print(f"[green]✓[/green] Within budget: {percentage:.1f}% of ${budget_usd:.2f}")


# =============================================================================
# EXAMPLES
# =============================================================================

def example_basic_logging():
    """Example: Basic usage logging"""
    console.print("\n[bold]Example 1: Basic Logging[/bold]\n")
    
    tracker = TokenTracker("example_usage.db")
    
    # Log some usage
    tracker.log("openai", "gpt-3.5-turbo", prompt_tokens=100, completion_tokens=50)
    tracker.log("anthropic", "claude-3-5-sonnet-20241022", prompt_tokens=200, completion_tokens=150)
    tracker.log("openai", "gpt-4", prompt_tokens=50, completion_tokens=25)
    
    console.print("[green]✓ Logged 3 requests[/green]")


def example_display_report():
    """Example: Display usage report"""
    console.print("\n[bold]Example 2: Usage Report[/bold]\n")
    
    tracker = TokenTracker("example_usage.db")
    tracker.display_report()


def example_recent_history():
    """Example: Show recent requests"""
    console.print("\n[bold]Example 3: Recent History[/bold]\n")
    
    tracker = TokenTracker("example_usage.db")
    tracker.display_recent(limit=5)


def example_budget_check():
    """Example: Budget checking"""
    console.print("\n[bold]Example 4: Budget Check[/bold]\n")
    
    tracker = TokenTracker("example_usage.db")
    tracker.check_budget(budget_usd=10.0, days=30)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    console.print("\n🎯 Project 3: Token Usage Tracker")
    console.print("=" * 60)
    
    try:
        example_basic_logging()
        example_display_report()
        example_recent_history()
        example_budget_check()
        
        console.print("\n" + "="*60)
        console.print("[green]✓ All examples completed![/green]")
        console.print("="*60)
        console.print("\n[bold]Next Steps:[/bold]")
        console.print("1. Integrate with Project 2 (Multi-Provider CLI)")
        console.print("2. Add budget alerts via email/Slack")
        console.print("3. Create usage optimization recommendations")
        console.print("4. Export reports to CSV/PDF")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        import traceback
        traceback.print_exc()
