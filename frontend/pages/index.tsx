import Head from 'next/head'

export default function Home() {
  return (
    <>
      <Head>
        <title>APEX Asia Property Exchange</title>
        <meta name="description" content="Asia Property Exchange CRM System" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              APEX Asia Property Exchange
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              CRM System for Property Management
            </p>
            <div className="bg-white rounded-lg shadow-md p-6 max-w-md mx-auto">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                System Status
              </h2>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Frontend:</span>
                  <span className="text-green-600 font-medium">✅ Running</span>
                </div>
                <div className="flex justify-between">
                  <span>Environment:</span>
                  <span className="text-blue-600 font-medium">
                    {process.env.NEXT_PUBLIC_ENVIRONMENT || 'development'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>API URL:</span>
                  <span className="text-gray-600 text-sm">
                    {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}
