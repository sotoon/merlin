import { useState, useEffect, useContext } from "react";
import { ErrorContext } from "../contexts/ErrorContext";

const useFetchData = (fetchFunction, setData) => {
  const [isLoading, setIsLoading] = useState(true);
  const { setErrorMessage } = useContext(ErrorContext);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetchFunction();
        console.log(
          `response status: ${response.status} response data: ${JSON.stringify(
            response.data,
          )}`,
        );
        setData(response.data);
      } catch (error) {
        console.error(error);
        setErrorMessage("A problem occurred. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [fetchFunction, setErrorMessage]);

  return isLoading;
};

export default useFetchData;
