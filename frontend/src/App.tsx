import { useState } from 'react'
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
} from '@chakra-ui/react'
import { createStandaloneToast } from '@chakra-ui/toast'
import { FiUpload, FiRefreshCw } from 'react-icons/fi'
import axios from 'axios'

const { toast, ToastContainer } = createStandaloneToast()

interface Flashcard {
  question: string
  answer: string
}

function App() {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [currentCardIndex, setCurrentCardIndex] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (file.type !== 'application/pdf') {
      toast({
        title: 'Invalid file type',
        description: 'Please upload a PDF file',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
      return
    }

    setIsLoading(true)
    const formData = new FormData()
    formData.append('pdf_file', file)

    try {
      const response = await axios.post('http://localhost:8080/api/generate-flashcards', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setFlashcards(response.data)
      setCurrentCardIndex(0)
      setShowAnswer(false)
      toast({
        title: 'Success',
        description: 'Flashcards generated successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    } catch (error: any) {
      console.error('Error details:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to generate flashcards'
      toast({
        title: 'Error',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsLoading(false)
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
      <ToastContainer />
      <Box minH="100vh" bg="gray.50" py={10}>
        <Container maxW="container.md">
          <VStack spacing={8}>
            <Heading>AI Notes Generator</Heading>
            <Text textAlign="center" color="gray.600">
              Upload a PDF document to generate AI-powered flashcards
            </Text>

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
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                  id="file-upload"
                />
                <label htmlFor="file-upload">
                  <Button
                    as="span"
                    leftIcon={<Icon as={FiUpload} />}
                    colorScheme="blue"
                    isLoading={isLoading}
                    loadingText="Generating Flashcards..."
                  >
                    Upload PDF
                  </Button>
                </label>
              </VStack>
            </Box>

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