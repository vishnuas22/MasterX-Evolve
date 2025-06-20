import React from 'react';
import { motion } from 'framer-motion';

export function GlassCard({ 
  children, 
  className = '', 
  animate = true, 
  hover = true,
  ...props 
}) {
  const baseClasses = `
    backdrop-blur-xl bg-white/5 
    border border-white/10 
    rounded-2xl shadow-2xl 
    ${className}
  `;

  const hoverClasses = hover ? 'hover:bg-white/10 hover:border-white/20 transition-all duration-300' : '';

  const Card = animate ? motion.div : 'div';

  const animationProps = animate ? {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5 }
  } : {};

  return (
    <Card
      className={`${baseClasses} ${hoverClasses}`}
      {...animationProps}
      {...props}
    >
      {children}
    </Card>
  );
}

export function GlassButton({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  className = '', 
  disabled = false,
  onClick,
  ...props 
}) {
  const baseClasses = `
    backdrop-blur-xl border rounded-xl font-medium
    transition-all duration-300 transform
    focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-transparent
    disabled:opacity-50 disabled:cursor-not-allowed
    active:scale-95
  `;

  const variants = {
    primary: `
      bg-gradient-to-r from-blue-500/20 to-purple-500/20 
      border-blue-400/30 text-blue-100
      hover:from-blue-500/30 hover:to-purple-500/30 
      hover:border-blue-400/50 hover:shadow-lg hover:shadow-blue-500/25
      focus:ring-blue-400/50
    `,
    secondary: `
      bg-white/5 border-white/20 text-gray-100
      hover:bg-white/10 hover:border-white/30
      focus:ring-white/50
    `,
    success: `
      bg-gradient-to-r from-green-500/20 to-emerald-500/20 
      border-green-400/30 text-green-100
      hover:from-green-500/30 hover:to-emerald-500/30 
      hover:border-green-400/50
      focus:ring-green-400/50
    `,
    danger: `
      bg-gradient-to-r from-red-500/20 to-pink-500/20 
      border-red-400/30 text-red-100
      hover:from-red-500/30 hover:to-pink-500/30 
      hover:border-red-400/50
      focus:ring-red-400/50
    `
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
    xl: 'px-8 py-4 text-xl'
  };

  return (
    <motion.button
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      disabled={disabled}
      onClick={onClick}
      {...props}
    >
      {children}
    </motion.button>
  );
}

export function GlassInput({ 
  className = '', 
  error = false,
  ...props 
}) {
  const baseClasses = `
    backdrop-blur-xl bg-white/5 border rounded-xl
    px-4 py-3 text-gray-100 placeholder-gray-400
    transition-all duration-300
    focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-transparent
  `;

  const normalClasses = `
    border-white/20 
    hover:border-white/30 hover:bg-white/10
    focus:border-blue-400/50 focus:bg-white/10 focus:ring-blue-400/50
  `;

  const errorClasses = `
    border-red-400/50 bg-red-500/10
    focus:border-red-400 focus:ring-red-400/50
  `;

  return (
    <input
      className={`${baseClasses} ${error ? errorClasses : normalClasses} ${className}`}
      {...props}
    />
  );
}
