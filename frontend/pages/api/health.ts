import type { NextApiRequest, NextApiResponse } from 'next'

export default function handler(
  _req: NextApiRequest,
  res: NextApiResponse
) {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    environment: process.env.ENVIRONMENT || 'development',
    service: 'frontend'
  })
}
