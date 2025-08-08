      PROGRAM SINE
      REAL X, PI
      INTEGER I
      PI = 4.0 * ATAN(1.0)
      DO I = 0, 10
         X = I * PI / 5.0
         WRITE(6,100) X, SIN(X)
  100 FORMAT('X = ', F5.2, ', SIN(X) = ', F8.5)
      END DO
      END
      