import React, { useState, useEffect } from 'react'
import {
  ChakraProvider,
  Box,
  VStack,
  Heading,
  Text,
  Button,
  Container,
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
  CardFooter,
  Icon,
  useToast,
} from '@chakra-ui/react'
import { FiUpload, FiRefreshCw } from 'react-icons/fi'
import axios from 'axios'
import './App.css'

interface Flashcard {
  question: string
  answer: string
}

interface FlashcardResponse {
  flashcards: Flashcard[]
}

// Create axios instance with base URL and timeout
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [flashcards, setFlashcards] = useState<Flashcard[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentCardIndex, setCurrentCardIndex] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)
  const [isBackendConnected, setIsBackendConnected] = useState(false)
  const toast = useToast()

  // Check backend connection on component mount
  useEffect(() => {
    const checkBackendConnection = async () => {
      try {
        const response = await api.get('/flashcards/health')
        if (response.status === 200) {
          setIsBackendConnected(true)
        }
      } catch (error) {
        setIsBackendConnected(false)
        console.error('Backend connection error:', error)
      }
    }

    checkBackendConnection()
  }, [])

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]
    if (selectedFile) {
      // Validate file type
      if (selectedFile.type !== 'application/pdf') {
        toast({
          title: 'Invalid file type',
          description: 'Please upload a PDF file',
          status: 'error',
          duration: 3000,
          isClosable: true,
        })
        return
      }
      
      // Validate file size (10MB limit)
      if (selectedFile.size > 10 * 1024 * 1024) {
        toast({
          title: 'File too large',
          description: 'Maximum file size is 10MB',
          status: 'error',
          duration: 3000,
          isClosable: true,
        })
        return
      }

      setFile(selectedFile)
      setError(null)
      toast({
        title: 'File selected',
        description: `${selectedFile.name} is ready to upload`,
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    }
  }

  const handleFileUpload = async () => {
    if (!file) {
      toast({
        title: 'No file selected',
        description: 'Please select a PDF file first',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
      return
    }

    if (!isBackendConnected) {
      toast({
        title: 'Backend not connected',
        description: 'Please ensure the backend server is running',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
      return
    }

    setLoading(true)
    setError(null)
    setFlashcards([])

    const formData = new FormData()
    formData.append('file', file)

    try {
      console.log('Uploading file:', file.name, 'Size:', file.size)
      
      const response = await api.post<FlashcardResponse>('/flashcards/generate', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // 2 minutes timeout
        maxContentLength: 10 * 1024 * 1024, // 10MB max file size
      })

      console.log('Response received:', response.status, response.data)

      if (response.status === 200 && response.data.flashcards) {
        setFlashcards(response.data.flashcards)
        setCurrentCardIndex(0)
        setShowAnswer(false)
        toast({
          title: 'Success',
          description: `Generated ${response.data.flashcards.length} flashcards`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
      } else {
        throw new Error('Invalid response format')
      }
    } catch (error) {
      console.error('Upload error:', error)
      
      if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNABORTED') {
          setError('Request timed out. Please try again later.')
        } else if (error.code === 'ERR_NETWORK') {
          setError('Network error. Please check your internet connection and ensure the backend server is running.')
        } else if (error.response) {
          setError(`Server error: ${error.response.data?.detail || error.message}`)
        } else if (error.request) {
          setError('No response from server. Please ensure the backend server is running.')
        } else {
          setError(`Error: ${error.message}`)
        }
      } else {
        setError('An unexpected error occurred. Please try again later.')
      }
      
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to generate flashcards',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const nextCard = () => {
    if (currentCardIndex < flashcards.length - 1) {
      setCurrentCardIndex(currentCardIndex + 1)
      setShowAnswer(false)
    }
  }

  const previousCard = () => {
    if (currentCardIndex > 0) {
      setCurrentCardIndex(currentCardIndex - 1)
      setShowAnswer(false)
    }
  }

  return (
    <ChakraProvider>
      <Box minH="100vh" bg="gray.50" py={10}>
        <Container maxW="container.md">
          <VStack spacing={8}>
            <Heading>AI Notes Generator</Heading>
            <Text textAlign="center" color="gray.600">
              Upload a PDF document to generate AI-powered flashcards
            </Text>

            {!isBackendConnected && (
              <Box p={4} bg="red.50" borderRadius="md" border="1px" borderColor="red.200">
                <Text color="red.500">
                  Backend server is not connected. Please ensure the backend server is running at http://localhost:8000
                </Text>
              </Box>
            )}

            <Box
              p={6}
              bg="white"
              borderRadius="lg"
              boxShadow="lg"
              border="1px"
              borderColor="gray.200"
              w="100%"
            >
              <VStack spacing={4}>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                  id="file-upload"
                />
                <label htmlFor="file-upload">
                  <Button
                    as="span"
                    leftIcon={<Icon as={FiUpload} />}
                    colorScheme="blue"
                    isLoading={loading}
                    loadingText="Generating Flashcards..."
                    isDisabled={!isBackendConnected}
                  >
                    {file ? `Upload ${file.name}` : 'Upload PDF'}
                  </Button>
                </label>
                {file && (
                  <Button
                    onClick={handleFileUpload}
                    colorScheme="green"
                    isLoading={loading}
                    loadingText="Generating..."
                    isDisabled={!isBackendConnected}
                  >
                    Generate Flashcards
                  </Button>
                )}
              </VStack>
            </Box>

            {error && (
              <Text color="red.500" mt={4}>
                {error}
              </Text>
            )}

            {flashcards.length > 0 && (
              <Card w="100%" bg="white" borderColor="gray.200">
                <CardHeader>
                  <Text fontSize="sm" color="gray.500">
                    Card {currentCardIndex + 1} of {flashcards.length}
                  </Text>
                </CardHeader>
                <CardBody>
                  <VStack spacing={4} align="stretch">
                    <Text fontSize="xl" fontWeight="bold">
                      {flashcards[currentCardIndex].question}
                    </Text>
                    {showAnswer && (
                      <Text fontSize="lg" color="blue.500">
                        {flashcards[currentCardIndex].answer}
                      </Text>
                    )}
                  </VStack>
                </CardBody>
                <CardFooter>
                  <SimpleGrid columns={3} spacing={4} w="100%">
                    <Button
                      onClick={previousCard}
                      isDisabled={currentCardIndex === 0}
                      leftIcon={<Icon as={FiRefreshCw} transform="rotate(180deg)" />}
                    >
                      Previous
                    </Button>
                    <Button
                      onClick={() => setShowAnswer(!showAnswer)}
                      colorScheme="blue"
                    >
                      {showAnswer ? 'Hide Answer' : 'Show Answer'}
                    </Button>
                    <Button
                      onClick={nextCard}
                      isDisabled={currentCardIndex === flashcards.length - 1}
                      rightIcon={<Icon as={FiRefreshCw} />}
                    >
                      Next
                    </Button>
                  </SimpleGrid>
                </CardFooter>
              </Card>
            )}
          </VStack>
        </Container>
      </Box>
    </ChakraProvider>
  )
}

export default App