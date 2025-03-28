#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Input Validation Module
Description: Provides functions for validating different types of user input
Author: PyWrite Sidecar
Date: 2025-03-28
"""

def validate_input(user_input, validation_type='text', min_length=0, max_length=None):
    """
    Validate user input based on specified validation type and constraints.
    
    Args:
        user_input (str): The input string to validate
        validation_type (str): Type of validation to perform ('text', 'email', 'number', 'alpha')
        min_length (int): Minimum allowed length
        max_length (int): Maximum allowed length (None for no limit)
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check length constraints first
    if len(user_input) < min_length:
        return False, f"Input must be at least {min_length} characters"
        
    if max_length and len(user_input) > max_length:
        return False, f"Input cannot exceed {max_length} characters"
    
    # Perform type-specific validation
    if validation_type == 'text':
        return True, ""
        
    elif validation_type == 'email':
        if '@' not in user_input or '.' not in user_input:
            return False, "Invalid email format"
        return True, ""
        
    elif validation_type == 'number':
        try:
            float(user_input)
            return True, ""
        except ValueError:
            return False, "Input must be a number"
            
    elif validation_type == 'alpha':
        if not user_input.isalpha():
            return False, "Input must contain only letters"
        return True, ""
        
    else:
        return False, f"Unknown validation type: {validation_type}"
