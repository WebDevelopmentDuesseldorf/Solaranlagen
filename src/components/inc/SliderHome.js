import React from 'react';

import { Swiper, SwiperSlide } from "swiper/react";
import SwiperCore, {
    EffectCoverflow,Pagination,Navigation
  } from 'swiper';


import 'swiper/swiper.scss'
import '../styles/swiper.css'
import "swiper/components/effect-coverflow/effect-coverflow.min.css"
import "swiper/components/pagination/pagination.min.css"
import "swiper/components/navigation/navigation.min.css"

import bochum_res_200 from '../images/test_bochum_res_200.png'
import dortmund_res_200 from '../images/test_dortmund_res_200.png'
import duesseldorf_res_200 from '../images/test_duesseldorf_res_200.png'
import duisburg_res_200 from '../images/test_duisburg_res_200.png'
import essen_res_200 from '../images/test_essen_res_200.png'
import koeln_res_200 from '../images/test_koeln_res_200.png'


SwiperCore.use([EffectCoverflow,Pagination,Navigation]);

function SliderHome() {
    return (
      <>
        <Swiper
          effect={"coverflow"}
          grabCursor={true}
          centeredSlides={true}
          slidesPerView={"auto"}
          coverflowEffect={{
            rotate: 50,
            stretch: 0,
            depth: 100,
            modifier: 1,
            slideShadows: true
          }}
          pagination={true}
          navigation={true}
          className="mySwiper"
        >
          <SwiperSlide>
            <img src={bochum_res_200} alt="Map Overview which shows the efficiency of solarpanel in the region Bochum"/>
          </SwiperSlide>
          <SwiperSlide>
            <img src={dortmund_res_200} alt="Map Overview which shows the efficiency of solarpanel in the region Dortmund"/>
          </SwiperSlide>
          <SwiperSlide>
            <img src={duesseldorf_res_200} alt="Map Overview which shows the efficiency of solarpanel in the region Duesseldorf"/>
          </SwiperSlide>
          <SwiperSlide>
            <img src={duisburg_res_200} alt="Map Overview which shows the efficiency of solarpanel in the region Duisburg"/>
          </SwiperSlide>
          <SwiperSlide>
            <img src={essen_res_200} alt="Map Overview which shows the efficiency of solarpanel in the region Essen"/>
          </SwiperSlide>
          <SwiperSlide>
            <img src={koeln_res_200} alt="Map Overview which shows the efficiency of solarpanel in the region Koeln"/>
          </SwiperSlide>
        </Swiper>
      </>
    )
  }
  
  export default SliderHome; 