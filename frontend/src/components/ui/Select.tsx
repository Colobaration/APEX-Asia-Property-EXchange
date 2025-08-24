/**
 * Базовый компонент выпадающего списка
 */

import React from 'react';
import { SelectProps } from '@/types';

const Select: React.FC<SelectProps> = ({
  options,
  value,
  onChange,
  placeholder,
  error,
  disabled = false,
  className = '',
  ...props
}) => {
  const baseClasses = 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed';
  
  const errorClasses = error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : '';
  
  const classes = `${baseClasses} ${errorClasses} ${className}`;

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (onChange) {
      onChange(e.target.value);
    }
  };

  return (
    <div className="w-full">
      <select
        className={classes}
        value={value}
        onChange={handleChange}
        disabled={disabled}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};

export default Select;
