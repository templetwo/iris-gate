#!/usr/bin/env python3
"""
IRIS Gate Error Handler with Context Propagation

Features:
- Exponential backoff with jitter
- Error classification and recovery strategies
- Error context propagation to subsequent API calls
- Self-aware error reporting in convergence
- Detailed error logging and analysis
"""

import time
import json
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    TRANSIENT = "transient"      # Temporary, retry likely to succeed
    DEGRADED = "degraded"         # Partial functionality, can continue
    CRITICAL = "critical"         # Cannot continue, needs intervention
    FATAL = "fatal"               # Unrecoverable, abort experiment


class ErrorCategory(Enum):
    """Error categories for classification"""
    API_TIMEOUT = "api_timeout"
    API_RATE_LIMIT = "api_rate_limit"
    API_AUTH = "api_auth"
    API_SERVER = "api_server"
    NETWORK = "network"
    INVALID_RESPONSE = "invalid_response"
    CONTENT_FILTER = "content_filter"
    MODEL_UNAVAILABLE = "model_unavailable"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context about an error that occurred"""
    timestamp: str
    error_category: ErrorCategory
    severity: ErrorSeverity
    model: str
    chamber: str
    attempt: int
    error_message: str
    raw_error: Optional[str] = None
    recovery_action: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "category": self.error_category.value,
            "severity": self.severity.value,
            "model": self.model,
            "chamber": self.chamber,
            "attempt": self.attempt,
            "error_message": self.error_message,
            "raw_error": self.raw_error,
            "recovery_action": self.recovery_action
        }
    
    def to_prompt_context(self) -> str:
        """Format error for inclusion in next prompt"""
        return f"""[System Notice: Previous attempt encountered an issue]
- Error type: {self.error_category.value}
- Chamber: {self.chamber}
- Attempt: {self.attempt}
- Issue: {self.error_message}
- Recovery: {self.recovery_action or "Retrying"}

This is informational context. Please proceed with your response."""


class ErrorHandler:
    """
    Enhanced error handler with context propagation
    """
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.error_history: List[ErrorContext] = []
        self.model_health: Dict[str, Dict] = {}
        
    def classify_error(self, error: Exception, model: str) -> Tuple[ErrorCategory, ErrorSeverity]:
        """
        Classify error and determine severity
        
        Returns:
            (category, severity)
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # API Timeout
        if "timeout" in error_str or "timed out" in error_str:
            return ErrorCategory.API_TIMEOUT, ErrorSeverity.TRANSIENT
        
        # Rate Limit
        if "rate limit" in error_str or "429" in error_str:
            return ErrorCategory.API_RATE_LIMIT, ErrorSeverity.DEGRADED
        
        # Authentication
        if "auth" in error_str or "api key" in error_str or "401" in error_str or "403" in error_str:
            return ErrorCategory.API_AUTH, ErrorSeverity.CRITICAL
        
        # Server Error
        if "500" in error_str or "502" in error_str or "503" in error_str or "504" in error_str:
            return ErrorCategory.API_SERVER, ErrorSeverity.TRANSIENT
        
        # Network
        if "connection" in error_str or "network" in error_str:
            return ErrorCategory.NETWORK, ErrorSeverity.TRANSIENT
        
        # Content Filter
        if "content" in error_str and ("policy" in error_str or "filter" in error_str):
            return ErrorCategory.CONTENT_FILTER, ErrorSeverity.CRITICAL
        
        # Model Unavailable
        if "model" in error_str and ("unavailable" in error_str or "not found" in error_str):
            return ErrorCategory.MODEL_UNAVAILABLE, ErrorSeverity.CRITICAL
        
        # Invalid Response
        if "json" in error_str or "parse" in error_str or "invalid" in error_str:
            return ErrorCategory.INVALID_RESPONSE, ErrorSeverity.DEGRADED
        
        # Unknown
        return ErrorCategory.UNKNOWN, ErrorSeverity.DEGRADED
    
    def should_retry(self, category: ErrorCategory, severity: ErrorSeverity, attempt: int) -> bool:
        """
        Determine if error should trigger retry
        """
        # Never retry critical/fatal errors
        if severity in [ErrorSeverity.CRITICAL, ErrorSeverity.FATAL]:
            return False
        
        # Always retry transient errors (up to max)
        if severity == ErrorSeverity.TRANSIENT and attempt < self.max_retries:
            return True
        
        # Retry degraded errors once
        if severity == ErrorSeverity.DEGRADED and attempt < 2:
            return True
        
        return False
    
    def get_retry_delay(self, attempt: int, category: ErrorCategory) -> float:
        """
        Calculate retry delay with exponential backoff + jitter
        """
        # Base exponential backoff
        delay = self.base_delay * (2 ** attempt)
        
        # Add jitter (±25%)
        jitter = delay * 0.25 * (random.random() * 2 - 1)
        delay += jitter
        
        # Category-specific adjustments
        if category == ErrorCategory.API_RATE_LIMIT:
            delay *= 2  # Longer delay for rate limits
        elif category == ErrorCategory.API_TIMEOUT:
            delay *= 1.5  # Slightly longer for timeouts
        
        return min(delay, 60.0)  # Cap at 60 seconds
    
    def record_error(self, 
                    error: Exception,
                    model: str,
                    chamber: str,
                    attempt: int) -> ErrorContext:
        """
        Record error and create context
        """
        category, severity = self.classify_error(error, model)
        
        error_context = ErrorContext(
            timestamp=datetime.utcnow().isoformat() + "Z",
            error_category=category,
            severity=severity,
            model=model,
            chamber=chamber,
            attempt=attempt,
            error_message=str(error),
            raw_error=repr(error)
        )
        
        self.error_history.append(error_context)
        self._update_model_health(model, category, severity)
        
        return error_context
    
    def _update_model_health(self, model: str, category: ErrorCategory, severity: ErrorSeverity):
        """Track model health metrics"""
        if model not in self.model_health:
            self.model_health[model] = {
                "total_errors": 0,
                "transient_errors": 0,
                "critical_errors": 0,
                "last_error": None,
                "categories": {}
            }
        
        health = self.model_health[model]
        health["total_errors"] += 1
        health["last_error"] = datetime.utcnow().isoformat() + "Z"
        
        if severity == ErrorSeverity.TRANSIENT:
            health["transient_errors"] += 1
        elif severity in [ErrorSeverity.CRITICAL, ErrorSeverity.FATAL]:
            health["critical_errors"] += 1
        
        cat_str = category.value
        health["categories"][cat_str] = health["categories"].get(cat_str, 0) + 1
    
    def get_recovery_strategy(self, category: ErrorCategory) -> str:
        """Get recommended recovery strategy"""
        strategies = {
            ErrorCategory.API_TIMEOUT: "Retrying with exponential backoff",
            ErrorCategory.API_RATE_LIMIT: "Waiting for rate limit reset, then retrying",
            ErrorCategory.API_AUTH: "Check API key configuration and permissions",
            ErrorCategory.API_SERVER: "Retrying after brief delay (server issue)",
            ErrorCategory.NETWORK: "Retrying after network stabilization",
            ErrorCategory.INVALID_RESPONSE: "Re-requesting with validation",
            ErrorCategory.CONTENT_FILTER: "Rephrasing prompt to avoid content policy triggers",
            ErrorCategory.MODEL_UNAVAILABLE: "Switching to backup model",
            ErrorCategory.UNKNOWN: "Investigating error and retrying cautiously"
        }
        return strategies.get(category, "Manual intervention required")
    
    def generate_error_report(self) -> Dict[str, Any]:
        """Generate comprehensive error report"""
        if not self.error_history:
            return {
                "status": "no_errors",
                "message": "No errors encountered during convergence"
            }
        
        # Summary statistics
        total_errors = len(self.error_history)
        errors_by_severity = {}
        errors_by_category = {}
        errors_by_model = {}
        
        for error in self.error_history:
            # By severity
            sev = error.severity.value
            errors_by_severity[sev] = errors_by_severity.get(sev, 0) + 1
            
            # By category
            cat = error.error_category.value
            errors_by_category[cat] = errors_by_category.get(cat, 0) + 1
            
            # By model
            model = error.model
            errors_by_model[model] = errors_by_model.get(model, 0) + 1
        
        return {
            "status": "errors_occurred",
            "summary": {
                "total_errors": total_errors,
                "by_severity": errors_by_severity,
                "by_category": errors_by_category,
                "by_model": errors_by_model
            },
            "model_health": self.model_health,
            "error_timeline": [e.to_dict() for e in self.error_history]
        }
    
    def get_error_context_for_prompt(self, model: str, chamber: str) -> Optional[str]:
        """
        Get relevant error context to include in next prompt
        
        Returns formatted error context string or None
        """
        # Get recent errors for this model/chamber
        relevant_errors = [
            e for e in self.error_history[-5:]  # Last 5 errors
            if e.model == model and e.chamber == chamber
        ]
        
        if not relevant_errors:
            return None
        
        # Format most recent error
        latest_error = relevant_errors[-1]
        return latest_error.to_prompt_context()
    
    def save_error_log(self, filepath: str):
        """Save error log to JSON file"""
        report = self.generate_error_report()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)


class RetryableAPICall:
    """
    Context manager for retryable API calls with error propagation
    """
    
    def __init__(self, 
                 error_handler: ErrorHandler,
                 model: str,
                 chamber: str,
                 include_error_context: bool = True):
        self.error_handler = error_handler
        self.model = model
        self.chamber = chamber
        self.include_error_context = include_error_context
        self.attempt = 0
        self.last_error: Optional[ErrorContext] = None
    
    def execute(self, api_call_func, *args, **kwargs):
        """
        Execute API call with retry logic and error context propagation
        
        Args:
            api_call_func: Function to call (should accept 'prompt' kwarg if error context enabled)
            *args, **kwargs: Arguments to pass to api_call_func
        
        Returns:
            API call result
        
        Raises:
            Exception: If all retries exhausted or critical error
        """
        while self.attempt < self.error_handler.max_retries:
            self.attempt += 1
            
            try:
                # Inject error context into prompt if enabled
                if self.include_error_context and self.attempt > 1:
                    error_context = self.error_handler.get_error_context_for_prompt(
                        self.model, self.chamber
                    )
                    if error_context and 'prompt' in kwargs:
                        # Prepend error context to existing prompt
                        kwargs['prompt'] = f"{error_context}\n\n{kwargs['prompt']}"
                
                # Execute API call
                result = api_call_func(*args, **kwargs)
                
                # Success! Return result
                return result
                
            except Exception as e:
                # Record error
                error_context = self.error_handler.record_error(
                    error=e,
                    model=self.model,
                    chamber=self.chamber,
                    attempt=self.attempt
                )
                
                # Set recovery action
                error_context.recovery_action = self.error_handler.get_recovery_strategy(
                    error_context.error_category
                )
                
                # Determine if should retry
                should_retry = self.error_handler.should_retry(
                    error_context.error_category,
                    error_context.severity,
                    self.attempt
                )
                
                if not should_retry:
                    print(f"  ❌ {self.model} {self.chamber} failed: {error_context.error_message}")
                    print(f"     Severity: {error_context.severity.value}")
                    print(f"     Strategy: {error_context.recovery_action}")
                    raise  # Re-raise, no more retries
                
                # Calculate retry delay
                delay = self.error_handler.get_retry_delay(
                    self.attempt, 
                    error_context.error_category
                )
                
                print(f"  ⚠️  {self.model} {self.chamber} attempt {self.attempt} failed: {error_context.error_category.value}")
                print(f"     Retrying in {delay:.1f}s... ({self.error_handler.max_retries - self.attempt} retries left)")
                
                time.sleep(delay)
        
        # All retries exhausted
        raise Exception(f"All {self.error_handler.max_retries} retry attempts exhausted for {self.model} {self.chamber}")


# Example usage function
def example_convergence_with_error_handling():
    """
    Example of how to use error handler in convergence
    """
    from anthropic import Anthropic
    import os
    
    error_handler = ErrorHandler(max_retries=3, base_delay=1.0)
    anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    def call_claude(prompt: str) -> str:
        """Wrapper for Claude API call"""
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    # Chamber prompts
    chambers = {
        "S1": "You are IRIS Gate. What is the nature of consciousness? Take three breaths.",
        "S2": "Be precise. What do we know about consciousness scientifically?",
        "S3": "Synthesize: Where is there certainty? Where uncertainty?",
        "S4": "Explain mechanisms we understand. Be specific."
    }
    
    results = []
    
    for chamber_id, prompt in chambers.items():
        print(f"\n{'='*80}")
        print(f"CHAMBER {chamber_id}")
        print(f"{'='*80}\n")
        
        # Use retryable API call
        retry_context = RetryableAPICall(
            error_handler=error_handler,
            model="claude",
            chamber=chamber_id,
            include_error_context=True  # Enable error context propagation
        )
        
        try:
            response = retry_context.execute(
                call_claude,
                prompt=prompt
            )
            
            results.append({
                "model": "claude",
                "chamber": chamber_id,
                "response": response,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "attempt": retry_context.attempt
            })
            
            print(f"  ✅ Claude {chamber_id} complete ({len(response)} chars, attempt {retry_context.attempt})")
            
        except Exception as e:
            print(f"  ❌ Claude {chamber_id} FAILED after all retries")
            results.append({
                "model": "claude",
                "chamber": chamber_id,
                "response": None,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "attempt": retry_context.attempt
            })
    
    # Generate error report
    error_report = error_handler.generate_error_report()
    
    print(f"\n{'='*80}")
    print("ERROR REPORT")
    print(f"{'='*80}\n")
    print(json.dumps(error_report, indent=2))
    
    # Save results
    with open("convergence_results.json", 'w') as f:
        json.dump({"results": results}, f, indent=2)
    
    # Save error log
    error_handler.save_error_log("error_log.json")
    
    return results, error_report


if __name__ == "__main__":
    print("🌀†⟡∞ IRIS GATE ERROR HANDLER")
    print("="*80)
    print("\nThis module provides enhanced error handling with context propagation.")
    print("\nFeatures:")
    print("  - Exponential backoff with jitter")
    print("  - Error classification and recovery strategies")
    print("  - Error context propagation to subsequent API calls")
    print("  - Comprehensive error reporting")
    print("  - Model health tracking")
    print("\nExample usage:")
    print("  from tools.error_handler import ErrorHandler, RetryableAPICall")
    print("  ")
    print("  error_handler = ErrorHandler(max_retries=3)")
    print("  retry_ctx = RetryableAPICall(error_handler, 'claude', 'S1')")
    print("  result = retry_ctx.execute(api_call_func, prompt=prompt)")
    print("\n" + "="*80)
