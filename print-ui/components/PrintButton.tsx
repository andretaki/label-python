'use client'

interface PrintButtonProps {
  onClick: () => void
  loading?: boolean
  disabled?: boolean
}

/**
 * Large print button with loading state.
 */
export function PrintButton({ onClick, loading, disabled }: PrintButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        w-full py-4 px-6 rounded-xl text-xl font-bold
        transition-all duration-200
        flex items-center justify-center gap-3
        ${disabled || loading
          ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
          : 'bg-alliance-purple text-white hover:bg-opacity-90 active:scale-[0.98] shadow-lg hover:shadow-xl'
        }
      `}
    >
      {loading ? (
        <>
          <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin" />
          Printing...
        </>
      ) : (
        <>
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
            />
          </svg>
          Print Labels
        </>
      )}
    </button>
  )
}
